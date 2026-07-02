# PDF Generator

A FastAPI web app that converts images (photos of notes, textbooks, whiteboards, etc.) into structured, print-ready A4 PDFs — with full support for mathematical expressions rendered in LaTeX and embedded diagrams.

## Features

- **Image to PDF** — Upload one or more images; the app extracts all text, math (LaTeX), and diagrams using the Gemini vision API, then renders a clean A4 PDF via headless Chromium.
- **Preview before download** — Extracted content is shown in a browser preview (MathJax renders LaTeX live) before the PDF is downloaded.
- **Google Drive upload** — After the user confirms the preview, the PDF is uploaded to a pre-configured Google Drive folder.

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
6. The PDF is also uploaded automatically to the configured Google Drive folder.

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Upload page |
| `POST` | `/pdf/generate` | Submit images; redirects to preview |
| `GET` | `/pdf/preview/{id}` | HTML preview of extracted content |
| `GET` | `/pdf/download/{id}` | Download the rendered PDF |

## Project structure

```
.
├── main.py                     # FastAPI app entry point
├── requirements.txt
├── .env.example
├── app/
│   ├── core/
│   │   └── config.py           # Settings (loaded from .env)
│   ├── routers/
│   │   └── pdf.py              # /pdf/* route handlers
│   ├── services/
│   │   ├── extraction.py       # Gemini vision API — text + LaTeX + diagram extraction
│   │   └── pdf_generator.py    # Playwright HTML → PDF
│   ├── templates/
│   │   ├── upload.html         # Image upload form
│   │   └── preview.html        # Preview + download (shared with Playwright)
│   └── static/
│       └── styles.css
```
