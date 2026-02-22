#!/usr/bin/env python3
"""Create a new tab in a Google Sheet and render an image as pixel art by cell background colors.

Uses gogcli-exported refresh token + client_id/secret.

Design goals:
- Few API calls: one batchUpdate for sheet creation + dimension sizing + cell formats.
- Quantize to an adaptive palette to keep colors stable.

NOTE: This writes formatting (background colors) only; values are left empty.
"""

import argparse
import json
import math
from pathlib import Path

from PIL import Image

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"


def a1_col(n: int) -> str:
    """1-indexed column number to A1 letters."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def load_creds(client_id: str, client_secret: str, refresh_token_path: Path) -> Credentials:
    tok = json.loads(refresh_token_path.read_text())
    refresh_token = tok.get("refresh_token") or tok.get("refreshToken")
    if not refresh_token:
        raise SystemExit(f"No refresh_token found in {refresh_token_path}")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[SHEETS_SCOPE],
    )
    creds.refresh(Request())
    return creds


def prepare_image(image_path: Path, size: int, palette: int, dither: str) -> Image.Image:
    im = Image.open(image_path).convert("RGB")

    # Fit within size x size (letterbox with white background)
    w, h = im.size
    scale = min(size / w, size / h)
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    im_resized = im.resize((nw, nh), resample=Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (size, size), (255, 255, 255))
    ox = (size - nw) // 2
    oy = (size - nh) // 2
    canvas.paste(im_resized, (ox, oy))

    dither_flag = Image.Dither.FLOYDSTEINBERG if dither.lower().startswith("floyd") else Image.Dither.NONE
    # Quantize via adaptive palette
    quant = canvas.quantize(colors=palette, method=Image.Quantize.MEDIANCUT, dither=dither_flag)
    return quant.convert("RGB")


def rgb_to_api_color(rgb):
    r, g, b = rgb
    return {"red": r / 255.0, "green": g / 255.0, "blue": b / 255.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spreadsheet", required=True)
    ap.add_argument("--title", required=True, help="New tab title")
    ap.add_argument("--image", required=True)
    ap.add_argument("--size", type=int, default=160, help="Grid size NxN")
    ap.add_argument("--palette", type=int, default=96, help="# colors")
    ap.add_argument("--cell_px", type=int, default=5, help="Row height / col width in pixels")
    ap.add_argument("--dither", default="floyd", choices=["floyd", "none"])
    ap.add_argument("--client_id", required=True)
    ap.add_argument("--client_secret", required=True)
    ap.add_argument("--refresh_token_json", required=True)
    args = ap.parse_args()

    creds = load_creds(args.client_id, args.client_secret, Path(args.refresh_token_json))
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)

    # Prepare pixel image
    pix = prepare_image(Path(args.image), args.size, args.palette, args.dither)
    size = args.size
    pixels = pix.load()

    # Create new sheet
    # If sheet exists, we'll error; caller can choose a different name.
    add_sheet_req = {
        "addSheet": {
            "properties": {
                "title": args.title,
                "gridProperties": {"rowCount": size, "columnCount": size, "frozenRowCount": 0, "frozenColumnCount": 0},
            }
        }
    }

    # We need sheetId for dimension updates + cell writes; so do a first batchUpdate to add the sheet.
    resp = svc.spreadsheets().batchUpdate(
        spreadsheetId=args.spreadsheet,
        body={"requests": [add_sheet_req], "includeSpreadsheetInResponse": True},
    ).execute()

    sheets = resp.get("updatedSpreadsheet", {}).get("sheets", [])
    sheet_id = None
    for sh in sheets:
        props = sh.get("properties", {})
        if props.get("title") == args.title:
            sheet_id = props.get("sheetId")
            break
    if sheet_id is None:
        raise SystemExit("Failed to locate new sheetId after creation")

    # Set row heights and column widths
    dim_reqs = []
    dim_reqs.append({
        "updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "ROWS", "startIndex": 0, "endIndex": size},
            "properties": {"pixelSize": args.cell_px},
            "fields": "pixelSize",
        }
    })
    dim_reqs.append({
        "updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": size},
            "properties": {"pixelSize": args.cell_px},
            "fields": "pixelSize",
        }
    })

    # Build cell data rows
    rows = []
    for y in range(size):
        row_vals = []
        for x in range(size):
            color = rgb_to_api_color(pixels[x, y])
            row_vals.append({
                "userEnteredFormat": {"backgroundColor": color},
            })
        rows.append({"values": row_vals})

    update_cells_req = {
        "updateCells": {
            "rows": rows,
            "fields": "userEnteredFormat.backgroundColor",
            "start": {"sheetId": sheet_id, "rowIndex": 0, "columnIndex": 0},
        }
    }

    # One final batch update for dimensions + all colors
    svc.spreadsheets().batchUpdate(
        spreadsheetId=args.spreadsheet,
        body={"requests": dim_reqs + [update_cells_req]},
    ).execute()

    # Print a helpful range link
    a1 = f"{a1_col(1)}1:{a1_col(size)}{size}"
    print(json.dumps({
        "ok": True,
        "sheetTitle": args.title,
        "sheetId": sheet_id,
        "grid": f"{args.title}!{a1}",
        "size": size,
        "palette": args.palette,
    }))


if __name__ == "__main__":
    main()
