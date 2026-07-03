# PDF Generator

A FastAPI web app that converts images (photos of notes, textbooks, whiteboards, etc.) into structured, print-ready A4 PDFs — with full support for mathematical expressions rendered in LaTeX and embedded diagrams.

## Features

- **Image to PDF** — Upload one or more images; the app extracts all text, math (LaTeX), and diagrams using the Gemini vision API, then renders a clean A4 PDF via headless Chromium.
- **Preview before download** — Extracted content is shown in a browser preview (MathJax renders LaTeX live) before the PDF is downloaded.
- **Google Drive upload** — From the preview page, an "Upload to Drive" button uploads the PDF to a pre-configured Google Drive folder.

## Tech stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI + Uvicorn |
| Vision / extraction | Gemini API (Google) via OpenAI SDK |
| PDF rendering | Playwright (headless Chromium) |
| Math rendering | MathJax 3 (CDN) |
| Templates | Jinja2 |
| Config | pydantic-settings + `.env` |

## Requirements

- Python 3.14.4
- A Gemini (Google AI Studio) API key

## Setup

```bash
# 1. Create and activate the virtual environment
python -m venv .venv-pdf-generator
source .venv-pdf-generator/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright's headless browser
playwright install chromium

# 4. Configure environment variables
cp .env.example .env
# Edit .env and fill in your GEMINI_API_KEY
```

### Environment variables

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Your Gemini API key | _(required)_ |
| `GEMINI_MODEL` | Gemini vision model to use | `gemini-2.5-flash` |
| `GOOGLE_DRIVE_FOLDER_ID` | Destination Drive folder ID for uploads | _(required)_ |
| `GOOGLE_OAUTH_CLIENT_SECRET_FILE` | Path to the OAuth client JSON | `client_secret.json` |
| `GOOGLE_OAUTH_TOKEN_FILE` | Path to the saved OAuth token | `token.json` |

## Google Drive setup

The "Upload to Drive" button uploads the generated PDF using **OAuth2 user credentials** (not a service account — service accounts have no storage quota on a regular "My Drive" folder, only on Shared Drives, which require Google Workspace). This is a one-time setup per machine.

### 1. Create a Google Cloud project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one) from the project picker at the top of the page.

### 2. Enable the Google Drive API

1. In the left sidebar, go to **APIs & Services → Library**.
2. Search for **Google Drive API** and open it.
3. Click **Enable**.

### 3. Configure the OAuth consent screen

1. Go to **APIs & Services → OAuth consent screen**.
2. Set **User Type** to **External** — this is required even for personal use; **Internal** only works for Google Workspace organizations and will cause `Error 403: org_internal` during authorization.
3. Fill in the required app details (app name, support email, developer contact email) and save.
4. Under **Test users**, click **Add users** and add the Google account you'll upload PDFs to.

### 4. Create an OAuth client

1. Go to **APIs & Services → Credentials**.
2. Click **Create Credentials → OAuth client ID**.
3. Set **Application type** to **Desktop app**, give it a name, and click **Create**.
4. Download the client JSON (**Download JSON** button after creation) and save it in the project root as `client_secret.json`. This file is gitignored.

### 5. Get the destination folder ID

1. Open the target Google Drive folder in your browser.
2. Copy the ID from the URL: `https://drive.google.com/drive/folders/<FOLDER_ID>`.
3. Set `GOOGLE_DRIVE_FOLDER_ID` in `.env` to that value.

### 6. Authorize the app

```bash
source .venv-pdf-generator/bin/activate
python scripts/authorize_drive.py
```

This opens a browser for you to sign in and consent, then saves a refresh token to `token.json` (gitignored). Re-run this script if `token.json` is ever deleted or revoked.

## Running

```bash
source .venv-pdf-generator/bin/activate
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

## Usage

1. Open the app at `http://localhost:8000`.
2. Upload one or more images (JPEG, PNG, etc.).
3. The app extracts text, math expressions (LaTeX), and diagrams from the images.
4. Review the formatted preview — MathJax renders all LaTeX in the browser.
5. Click **Download PDF** to get the A4 print-ready PDF.
6. Click **Upload to Drive** to upload the PDF to the configured Google Drive folder (see [Google Drive setup](#google-drive-setup)); success shows a "View in Drive" link inline on the preview page.

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Upload page |
| `POST` | `/pdf/generate` | Submit images; redirects to preview |
| `GET` | `/pdf/preview/{id}` | HTML preview of extracted content |
| `GET` | `/pdf/download/{id}` | Download the rendered PDF |
| `POST` | `/pdf/upload/{id}` | Upload the rendered PDF to Google Drive |

## Project structure

```
.
├── main.py                     # FastAPI app entry point
├── requirements.txt
├── .env.example
├── scripts/
│   └── authorize_drive.py      # One-time OAuth2 consent flow; writes token.json
├── app/
│   ├── core/
│   │   └── config.py           # Settings (loaded from .env)
│   ├── routers/
│   │   └── pdf.py              # /pdf/* route handlers
│   ├── services/
│   │   ├── extraction.py           # Gemini vision API — text + LaTeX + diagram extraction
│   │   ├── content_formatting.py   # Strips reference tags, splits numbered problem groups
│   │   ├── pdf_generator.py        # Playwright HTML → PDF
│   │   └── drive_upload.py         # Uploads rendered PDF to Google Drive via OAuth2
│   ├── templates/
│   │   ├── upload.html         # Image upload form
│   │   └── preview.html        # Preview + download + "Upload to Drive" (shared with Playwright)
│   └── static/
│       └── styles.css
```
