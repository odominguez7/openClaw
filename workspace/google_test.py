from googleapiclient.discovery import build
from google.auth import default

creds, _ = default()

service = build("docs", "v1", credentials=creds)

DOCUMENT_ID = "1qTjh00s8X1doiCg27yqyWBnD5qBfl9dT1evkHkciFRc"

doc = service.documents().get(documentId=DOCUMENT_ID).execute()

print("Title:", doc.get("title"))
