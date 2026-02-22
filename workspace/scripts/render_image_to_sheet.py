#!/usr/bin/env python3
"""Render an image into a Google Sheets tab as pixel art via cell background colors.

Usage:
  python3 render_image_to_sheet.py --image /path/to/image.jpg --sheet-title "12) Photo" \
    --width 100 --height 100 --pixel-size 10 --mode contain

Notes:
- Uses OAuth token at /home/odominguez7/okr-bot/token.json
- Spreadsheet ID is hard-coded to Omar's OKR sheet.
"""

import argparse
import math
import os
from typing import Tuple

from PIL import Image
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "1JZafCoPUILYq3R3E5lJkJAhnevvj2UkQWZkrlML55hM"
TOKEN_PATH = "/home/odominguez7/okr-bot/token-sheets.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def a1_col(n: int) -> str:
    """1-indexed column number -> A1 column letters."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build("sheets", "v4", credentials=creds)


def ensure_sheet(service, title: str) -> int:
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    for sh in meta.get("sheets", []):
        props = sh.get("properties", {})
        if props.get("title") == title:
            return props["sheetId"]

    # Create new sheet
    resp = (
        service.spreadsheets()
        .batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
        )
        .execute()
    )
    return resp["replies"][0]["addSheet"]["properties"]["sheetId"]


def clear_and_resize_grid(service, sheet_id: int, width: int, height: int, pixel_size: int):
    # Ensure the grid is large enough, then clear formats/values.
    requests = [
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {
                        "rowCount": max(100, height),
                        "columnCount": max(26, width),
                        "frozenRowCount": 0,
                        "frozenColumnCount": 0,
                    },
                },
                "fields": "gridProperties(rowCount,columnCount,frozenRowCount,frozenColumnCount)",
            }
        },
        {"updateCells": {"range": {"sheetId": sheet_id}, "fields": "userEnteredValue,userEnteredFormat"}},
        # Set row heights
        {
            "updateDimensionProperties": {
                "range": {"sheetId": sheet_id, "dimension": "ROWS", "startIndex": 0, "endIndex": height},
                "properties": {"pixelSize": pixel_size},
                "fields": "pixelSize",
            }
        },
        # Set column widths
        {
            "updateDimensionProperties": {
                "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": width},
                "properties": {"pixelSize": pixel_size},
                "fields": "pixelSize",
            }
        },
    ]

    service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body={"requests": requests}).execute()


def resize_image(img: Image.Image, width: int, height: int, mode: str) -> Image.Image:
    img = img.convert("RGB")
    if mode == "stretch":
        return img.resize((width, height), Image.Resampling.LANCZOS)

    # contain: preserve aspect ratio, pad with edge-average color
    iw, ih = img.size
    scale = min(width / iw, height / ih)
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)

    # background color = average of image (simple)
    small = img.resize((1, 1), Image.Resampling.BOX)
    bg = small.getpixel((0, 0))
    canvas = Image.new("RGB", (width, height), bg)
    ox = (width - nw) // 2
    oy = (height - nh) // 2
    canvas.paste(resized, (ox, oy))
    return canvas


def build_update_cells_request(sheet_id: int, pixels, width: int, height: int):
    rows = []
    for y in range(height):
        row = {"values": []}
        for x in range(width):
            r, g, b = pixels[x, y]
            row["values"].append(
                {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": r / 255.0, "green": g / 255.0, "blue": b / 255.0}
                    }
                }
            )
        rows.append(row)

    return {
        "updateCells": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": height, "startColumnIndex": 0, "endColumnIndex": width},
            "rows": rows,
            "fields": "userEnteredFormat.backgroundColor",
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--sheet-title", required=True)
    ap.add_argument("--width", type=int, default=100)
    ap.add_argument("--height", type=int, default=100)
    ap.add_argument("--pixel-size", type=int, default=10)
    ap.add_argument("--mode", choices=["contain", "stretch"], default="contain")
    args = ap.parse_args()

    if not os.path.exists(args.image):
        raise SystemExit(f"Image not found: {args.image}")

    service = get_service()
    sheet_id = ensure_sheet(service, args.sheet_title)

    img = Image.open(args.image)
    img2 = resize_image(img, args.width, args.height, args.mode)
    pixels = img2.load()

    clear_and_resize_grid(service, sheet_id, args.width, args.height, args.pixel_size)

    # Build and send pixel updates. Keep under API limits by chunking rows.
    requests = []
    chunk = 20  # rows per request
    for y0 in range(0, args.height, chunk):
        y1 = min(args.height, y0 + chunk)
        rows = []
        for y in range(y0, y1):
            row = {"values": []}
            for x in range(args.width):
                r, g, b = pixels[x, y]
                row["values"].append(
                    {"userEnteredFormat": {"backgroundColor": {"red": r / 255.0, "green": g / 255.0, "blue": b / 255.0}}}
                )
            rows.append(row)
        requests.append(
            {
                "updateCells": {
                    "range": {"sheetId": sheet_id, "startRowIndex": y0, "endRowIndex": y1, "startColumnIndex": 0, "endColumnIndex": args.width},
                    "rows": rows,
                    "fields": "userEnteredFormat.backgroundColor",
                }
            }
        )

    # Execute in batches to avoid oversized payloads
    batch_size = 5
    for i in range(0, len(requests), batch_size):
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": requests[i : i + batch_size]},
        ).execute()

    end_col = a1_col(args.width)
    print(f"Rendered {args.width}x{args.height} pixel art to sheet '{args.sheet_title}' range A1:{end_col}{args.height} (pixelSize={args.pixel_size}).")


if __name__ == "__main__":
    main()
