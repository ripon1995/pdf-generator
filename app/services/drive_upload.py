import asyncio
import io
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from app.core.config import settings

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_credentials() -> Credentials:
    token_path = Path(settings.google_oauth_token_file)
    if not token_path.exists():
        raise RuntimeError(
            f"No Drive authorization found at {token_path}. "
            "Run `python scripts/authorize_drive.py` once to authorize this app."
        )
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json())
    return creds


def _upload(pdf_bytes: bytes, filename: str) -> dict:
    creds = _get_credentials()
    service = build("drive", "v3", credentials=creds)
    media = MediaIoBaseUpload(io.BytesIO(pdf_bytes), mimetype="application/pdf")
    file_metadata = {"name": filename, "parents": [settings.google_drive_folder_id]}
    return (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, webViewLink")
        .execute()
    )


async def upload_pdf_to_drive(pdf_bytes: bytes, filename: str) -> dict:
    """Returns {"id": ..., "webViewLink": ...}."""
    return await asyncio.to_thread(_upload, pdf_bytes, filename)
