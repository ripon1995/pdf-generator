"""One-time setup: authorize this app to upload to your Google Drive.

Run: python scripts/authorize_drive.py

Opens a browser for you to sign in and consent, then saves a refresh token to
GOOGLE_OAUTH_TOKEN_FILE so the app can upload PDFs without further interaction.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google_auth_oauthlib.flow import InstalledAppFlow

from app.core.config import settings
from app.services.drive_upload import SCOPES


def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        settings.google_oauth_client_secret_file, SCOPES
    )
    creds = flow.run_local_server(port=0)
    Path(settings.google_oauth_token_file).write_text(creds.to_json())
    print(f"Authorized. Token saved to {settings.google_oauth_token_file}")


if __name__ == "__main__":
    main()
