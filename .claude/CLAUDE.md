# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

- Python 3.14.4 (pinned in `.python-version`)
- Virtual environment: `.venv-pdf-generator/`
- Activate: `source .venv-pdf-generator/bin/activate`

## Running the app

```bash
source .venv-pdf-generator/bin/activate
uvicorn main:app --reload
```

App runs at `http://localhost:8000`.

## Setup (first time)

```bash
source .venv-pdf-generator/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # then fill in GEMINI_API_KEY and GOOGLE_DRIVE_FOLDER_ID
```

Google Drive upload (Feature 2) uses OAuth2, authorized once per machine:

1. In Google Cloud Console, create an OAuth client (type: Desktop app) with the Drive API enabled, and make sure the OAuth consent screen's User Type is **External** (not Internal — Internal only works for Workspace orgs) with your Google account added as a test user.
2. Download the client JSON as `client_secret.json` in the project root (gitignored).
3. Run `python scripts/authorize_drive.py` once — opens a browser for consent and saves `token.json` (gitignored). Re-run it if `token.json` is ever deleted or revoked.

## Stack

- **FastAPI** + **Uvicorn** — web framework and ASGI server
- **Pydantic / pydantic-settings** — models and config from `.env`
- **OpenAI SDK** — used to call the Gemini vision API (Google) via its OpenAI-compatible endpoint at `https://generativelanguage.googleapis.com/v1beta/openai/`
- **Playwright** — headless Chromium for HTML → A4 PDF rendering
- **Jinja2** — server-side HTML templates
- **MathJax 3 (CDN)** — LaTeX rendering in both browser preview and PDF

## Project Structure

See `.claude/project-rule.md` for the full directory layout. Key conventions:

- `app/routers/` — API route handlers
- `app/services/` — business logic (PDF generation, Drive upload)
- `app/models/` — Pydantic request/response schemas
- `app/templates/` + `app/static/` — Jinja2 HTML templates and CSS
- `app/core/` — config, logging, shared dependencies

## Features

### Feature 1 — Image to PDF
Accept one or more images, extract all content (mathematical expressions in LaTeX format + diagrams), and generate an A4 print-ready PDF. The user previews the output before downloading. See `.claude/feature-1-image-to-pdf.md` for full spec.

### Feature 2 — Google Drive Upload
From the preview page, an "Upload to Drive" button uploads the generated PDF to a pre-configured Google Drive folder (folder ID via `GOOGLE_DRIVE_FOLDER_ID`) using OAuth2 user credentials (not a service account — service accounts have no storage quota on regular "My Drive" folders, only on Shared Drives). See `.claude/feature-2-google-drive-upload.md` for full spec.

## Key files

- `main.py` — FastAPI app entry point; mounts `/static`, includes `pdf` router, serves upload page at `/`
- `app/core/config.py` — `Settings` loaded from `.env` via pydantic-settings (`GEMINI_API_KEY`, `GEMINI_MODEL`)
- `app/services/extraction.py` — calls Gemini vision API to extract text + LaTeX math; returns `(content, has_diagram)`
- `app/services/content_formatting.py` — `format_content()`: strips board/admission-exam reference tags and splits numbered problem groups into `.content-group` divs
- `app/services/pdf_generator.py` — takes rendered HTML string, runs Playwright headless Chromium, returns A4 PDF bytes
- `app/routers/pdf.py` — four routes: `POST /pdf/generate`, `GET /pdf/preview/{id}`, `GET /pdf/download/{id}`, `POST /pdf/upload/{id}` (Drive upload); sessions held in memory dict
- `app/services/drive_upload.py` — `upload_pdf_to_drive()`: loads OAuth2 credentials from `token.json` (auto-refreshing), uploads PDF bytes into `GOOGLE_DRIVE_FOLDER_ID` via the Drive API
- `scripts/authorize_drive.py` — one-time interactive script that runs the OAuth consent flow and writes `token.json`
- `app/templates/preview.html` — shared template for browser preview and Playwright PDF; MathJax renders LaTeX; also has the "Upload to Drive" button/JS
- `.env.example` — template for required env vars (copy to `.env`)
- `.gitignore` — excludes `.env`, venv, pycache, IDE files, `client_secret*.json`, `token.json`