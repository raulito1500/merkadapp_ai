import os.path
import base64
import zipfile
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from services.invoices.agent import run_invoice_agent


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_PATH = "credentials.json"
TOKEN_PATH = "token.json"


def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def list_invoice_messages() -> list[dict]:
    service = get_gmail_service()
    messages: list[dict] = []
    page_token = None

    while True:
        response = (
            service.users()
            .messages()
            .list(userId="me", q="label:facturas is:unread after:2023/1/1 before:2024/1/1", pageToken=page_token)
            .execute()
        )
        messages.extend(response.get("messages", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return messages


def get_message_headers(service, message_id: str) -> dict[str, str]:
    message = service.users().messages().get(
        userId="me",
        id=message_id,
        format="metadata",
        metadataHeaders=["From", "Subject"],
    ).execute()
    headers = message.get("payload", {}).get("headers", [])
    return {h["name"]: h["value"] for h in headers}


def _walk_parts(parts: list[dict]):
    for part in parts:
        if part.get("parts"):
            yield from _walk_parts(part["parts"])
        else:
            yield part


def find_zip_attachment(service, message_id: str) -> bytes | None:
    message = service.users().messages().get(
        userId="me", id=message_id, format="full").execute()
    parts = message.get("payload", {}).get("parts", [])
    for part in _walk_parts(parts):
        filename = part.get("filename", "")

        if filename.lower().endswith(".zip"):
            body = part["body"]
            if "attachmentId" in body:
                attachment = service.users().messages().attachments().get(
                    userId="me", messageId=message_id, id=body["attachmentId"]).execute()
                data = attachment["data"]
            else:
                data = body["data"]
            return base64.urlsafe_b64decode(data)
    return None


def extract_xml_from_zip(zip_bytes: bytes) -> bytes:
    zip_file_like = io.BytesIO(zip_bytes)

    with zipfile.ZipFile(zip_file_like) as zf:
        for name in zf.namelist():
            if name.lower().endswith(".xml"):
                return zf.read(name)

    raise ValueError("El ZIP no contiene ningún archivo .xml")


def parse_invoice_subject(subject: str) -> dict:
    parts = [p.strip() for p in subject.split(";") if p.strip()]
    nit, business_name = parts[0], parts[1]
    return {"nit": nit, "business_name": business_name}


if __name__ == "__main__":
    service = get_gmail_service()
    messages = list_invoice_messages()
    print(f"Encontrados {len(messages)} correos con la etiqueta facturas")

    primero = messages[0]
    headers = get_message_headers(service, primero["id"])
    business_name = parse_invoice_subject(headers["Subject"])["business_name"]

    try:
        result = run_invoice_agent(service, primero["id"], business_name)
        print(result)
    except Exception as e:
        print(e)
