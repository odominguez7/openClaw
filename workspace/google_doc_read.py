from googleapiclient.discovery import build
from google.auth import default

DOCUMENT_ID = "1qTjh00s8X1doiCg27yqyWBnD5qBfl9dT1evkHkciFRc"

def read_doc_plaintext(document_id: str) -> str:
    creds, _ = default()
    docs = build("docs", "v1", credentials=creds)

    doc = docs.documents().get(documentId=document_id).execute()
    content = doc.get("body", {}).get("content", [])

    out = []
    for element in content:
        para = element.get("paragraph")
        if not para:
            continue
        for pe in para.get("elements", []):
            tr = pe.get("textRun")
            if tr and "content" in tr:
                out.append(tr["content"])

    return "".join(out)

if __name__ == "__main__":
    text = read_doc_plaintext(DOCUMENT_ID)
    print(text[:1500])  # preview first 1500 chars
    print("\n---\nLEN:", len(text))

