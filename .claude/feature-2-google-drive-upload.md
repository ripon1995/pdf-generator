# Feature 2: Google Drive Upload

## Overview

After the PDF is successfully generated (Feature 1 complete), upload it to a specific Google Drive location.

## Requirements

- Upload is triggered only after Feature 1 succeeds (PDF generated and confirmed by user via preview)
- Upload destination is a **specific, pre-configured Google Drive folder link**
- Uses the Google Drive API for upload

## Flow

1. Feature 1 generates and previews the PDF
2. User reviews the preview, then clicks the **"Upload to Drive"** button (separate from "Download PDF") — this is the confirmation step
3. Upload to the configured Google Drive folder is triggered via `POST /pdf/upload/{session_id}`
4. Upload success (with a "View in Drive" link) or failure is shown inline on the preview page, without navigating away

## Implementation

- `app/services/drive_upload.py` — `upload_pdf_to_drive()` builds the PDF via the same render/`generate_pdf` path as download, then uploads it
- `app/routers/pdf.py` — `POST /pdf/upload/{session_id}` returns the standard `{success, data, message, error}` envelope
- `app/templates/preview.html` — button + inline `fetch()` JS

## Notes

- The target Google Drive folder ID is configurable via `GOOGLE_DRIVE_FOLDER_ID` in `.env`
- **Auth: OAuth2 user credentials, not a service account.** A service account was tried first but rejected — service accounts have no storage quota of their own, so uploads to a regular "My Drive" folder fail with `storageQuotaExceeded` (they only work against Shared Drives, which require Google Workspace). Since the target account is a personal Gmail account, OAuth2 is required so uploads count against the authorizing user's own quota.
- One-time setup: create a Desktop-app OAuth client in Google Cloud Console (consent screen User Type must be **External**, with the user added as a test user — **Internal** causes an `Error 403: org_internal`), save it as `client_secret.json`, then run `python scripts/authorize_drive.py` to produce `token.json`. Both files are gitignored. See `.claude/CLAUDE.md` for the full setup steps.