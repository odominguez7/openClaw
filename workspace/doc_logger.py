import base64
import json
import os
from datetime import datetime

import httplib2
from google.auth import default
from google_auth_httplib2 import AuthorizedHttp
from google.oauth2 import service_account
from googleapiclient.discovery import build

DOC_ID = "1qTjh00s8X1doiCg27yqyWBnD5qBfl9dT1evkHkciFRc"
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

_DOCS = None


def _get_creds():
    b64 = os.getenv("GOOGLE_SA_KEY_B64")
    if b64:
        info = json.loads(base64.b64decode(b64).decode("utf-8"))
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    creds, _ = default(scopes=SCOPES)
    return creds


def _get_docs_client():
    global _DOCS
    if _DOCS is not None:
        return _DOCS
    creds = _get_creds()
    http = AuthorizedHttp(creds, http=httplib2.Http(timeout=20))
    _DOCS = build("docs", "v1", http=http, cache_discovery=False)
    return _DOCS


def append_to_doc(sender, message):
    docs = _get_docs_client()

    text = (
        f"{datetime.now().isoformat(timespec='seconds')}\n"
        f"From: {sender}\n"
        f"Message: {message}\n\n"
    )

    # Append near end of doc (before final newline)
    doc = docs.documents().get(documentId=DOC_ID).execute()
    end_index = doc["body"]["content"][-1]["endIndex"] - 1

    docs.documents().batchUpdate(
        documentId=DOC_ID,
        body={
            "requests": [{
                "insertText": {
                    "location": {"index": end_index},
                    "text": text
                }
            }]
        }
    ).execute()

    return "Logged to Google Doc ✅"
