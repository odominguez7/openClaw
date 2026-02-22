#!/usr/bin/env python3
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1JZafCoPUILYq3R3E5lJkJAhnevvj2UkQWZkrlML55hM"
TAB_TITLE = "10) AI Studio HW1"
TOKEN_PATH = "/home/odominguez7/okr-bot/token.json"
SNAPSHOT_PATH = "/home/odominguez7/.openclaw/workspace/memory/mit_ai_studio_hw1_snapshot.json"

# We restore within A..EB (132 cols) for two blocks:
# - rows 1-56 (0-55)
# - rows 62-91 (61-90)

BG_DEFAULT = {"red": 1, "green": 1, "blue": 1}  # white


def main():
    snap = json.load(open(SNAPSHOT_PATH))
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    svc = build("sheets", "v4", credentials=creds)

    # Find sheetId
    meta = svc.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_id = None
    for s in meta.get("sheets", []):
        if s["properties"]["title"] == TAB_TITLE:
            sheet_id = s["properties"]["sheetId"]
            break
    if sheet_id is None:
        raise SystemExit(f"Tab not found: {TAB_TITLE}")

    requests = []

    # Clear text values in the two ranges
    def clear_values(a1range, rows, cols):
        blank = [["" for _ in range(cols)] for __ in range(rows)]
        svc.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{TAB_TITLE}'!{a1range}",
            valueInputOption="RAW",
            body={"values": blank},
        ).execute()

    # Apply background fill for an entire rectangular region
    def paint_bg(start_row, end_row, start_col, end_col, color):
        requests.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": start_row,
                        "endRowIndex": end_row,
                        "startColumnIndex": start_col,
                        "endColumnIndex": end_col,
                    },
                    "cell": {"userEnteredFormat": {"backgroundColor": color}},
                    "fields": "userEnteredFormat.backgroundColor",
                }
            }
        )

    # Restore each block: first paint whole region white, then paint pixel runs for non-white cells
    for b in snap["blocks"]:
        start_row = b["startRow"]
        rows = b["numRows"]
        cols = 132  # force A..EB
        end_row = start_row + rows

        # Paint region white
        paint_bg(start_row, end_row, 0, cols, BG_DEFAULT)

        # Build per-row runs from sparse cells list
        by_row = {}
        for cell in b["cells"]:
            r = cell["r"]
            c = cell["c"]
            by_row.setdefault(r, {})[c] = cell["bg"]

        for r in range(start_row, end_row):
            row_map = by_row.get(r, {})
            if not row_map:
                continue
            # Convert to runs by scanning 0..131 and using the color at each c (default None)
            c = 0
            while c < cols:
                bg = row_map.get(c)
                if bg is None:
                    c += 1
                    continue
                start_c = c
                color = bg
                c += 1
                while c < cols and row_map.get(c) == color:
                    c += 1
                end_c = c
                requests.append(
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": r,
                                "endRowIndex": r + 1,
                                "startColumnIndex": start_c,
                                "endColumnIndex": end_c,
                            },
                            "cell": {"userEnteredFormat": {"backgroundColor": color}},
                            "fields": "userEnteredFormat.backgroundColor",
                        }
                    }
                )

    # Batch update in chunks
    CHUNK = 400
    for i in range(0, len(requests), CHUNK):
        svc.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body={"requests": requests[i : i + CHUNK]}
        ).execute()

    # Clear values after colors (keeps it looking like pure pixel art)
    clear_values("A1:EB56", 56, 132)
    clear_values("A62:EB91", 30, 132)

    print("OK restored MIT_AI_STUDIO_HW1")


if __name__ == "__main__":
    main()
