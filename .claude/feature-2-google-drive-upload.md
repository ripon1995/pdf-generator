# Feature 2: Google Drive Upload

## Overview

After the PDF is successfully generated (Feature 1 complete), upload it to a specific Google Drive location.

## Requirements

- Upload is triggered only after Feature 1 succeeds (PDF generated and confirmed by user via preview)
- Upload destination is a **specific, pre-configured Google Drive folder link**
- Uses the Google Drive API for upload

## Flow

1. Feature 1 generates and previews the PDF
2. User confirms → PDF download is available
3. Upload to the configured Google Drive folder is triggered
4. Confirm upload success to the user

## Notes

- The target Google Drive folder URL/ID should be configurable (e.g. via environment variable)
- Requires Google Drive API credentials (OAuth2 or service account)