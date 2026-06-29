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
cp .env.example .env   # then fill in GROK_API_KEY
```

## Stack

- **FastAPI** + **Uvicorn** — web framework and ASGI server
- **Pydantic / pydantic-settings** — models and config from `.env`
- **OpenAI SDK** — used to call the Grok (xAI) vision API at `https://api.x.ai/v1`
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
After the PDF is confirmed via preview, upload it to a pre-configured Google Drive folder (folder ID via environment variable). Requires Google Drive API credentials (OAuth2 or service account). See `.claude/feature-2-google-drive-upload.md` for full spec.

## Key files

- `main.py` — FastAPI app entry point; mounts `/static`, includes `pdf` router, serves upload page at `/`
- `app/core/config.py` — `Settings` loaded from `.env` via pydantic-settings (`GROK_API_KEY`, `GROK_MODEL`)
- `app/services/extraction.py` — calls Grok vision API to extract text + LaTeX math; returns `(content, has_diagram)`
- `app/services/pdf_generator.py` — takes rendered HTML string, runs Playwright headless Chromium, returns A4 PDF bytes
- `app/routers/pdf.py` — three routes: `POST /pdf/generate`, `GET /pdf/preview/{id}`, `GET /pdf/download/{id}`; sessions held in memory dict
- `app/templates/preview.html` — shared template for browser preview and Playwright PDF; MathJax renders LaTeX
- `.env.example` — template for required env vars (copy to `.env`)
- `.gitignore` — excludes `.env`, venv, pycache, IDE files