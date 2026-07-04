import base64
import io
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.core.errors import ExtractionError
from app.services.content_formatting import format_content
from app.services.drive_upload import upload_pdf_to_drive
from app.services.extraction import GEMINI_MODEL_IDS, GEMINI_MODELS, extract_from_image
from app.services.image_normalization import normalize_image
from app.services.pdf_generator import generate_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf", tags=["pdf"])

_jinja = Environment(loader=FileSystemLoader("app/templates"), autoescape=True)

_sessions: dict[str, dict] = {}

# Inlined (not linked/referenced by <img src>/<script src>) so Playwright's
# page.set_content() — which has no page origin to resolve a relative URL against,
# and whose null origin makes Chromium block cross-origin CDN scripts served with
# Cross-Origin-Resource-Policy: same-origin (e.g. jsdelivr) — still renders styled,
# math-typeset output.
_CSS = Path("app/static/styles.css").read_text()
_LOGO_SVG = Path("app/static/logo.svg").read_text()
_MATHJAX_JS = Path("app/static/vendor/mathjax/tex-svg.js").read_text()


def _render(results: list[dict], session_id: str, chapter: str) -> str:
    formatted = [{**r, "content": format_content(r["content"])} for r in results]
    return _jinja.get_template("preview.html").render(
        results=formatted,
        session_id=session_id,
        inline_css=_CSS,
        logo_svg=_LOGO_SVG,
        mathjax_js=_MATHJAX_JS,
        chapter=chapter,
    )


def _render_header(chapter: str) -> str:
    return _jinja.get_template("pdf_header.html").render(chapter=chapter, logo_svg=_LOGO_SVG)


_PROVIDERS = {"gemini", "huggingface"}


@router.post("/generate")
async def generate(
    images: list[UploadFile] = File(...),
    chapter: str = Form(...),
    provider: str = Form("gemini"),
    gemini_model: str = Form(settings.gemini_model),
):
    if not images:
        raise HTTPException(status_code=400, detail="No images provided.")
    if provider not in _PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unknown extraction provider: {provider}")
    if provider == "gemini" and gemini_model not in GEMINI_MODEL_IDS:
        raise HTTPException(status_code=400, detail=f"Unknown Gemini model: {gemini_model}")

    model = gemini_model if provider == "gemini" else None
    results = []
    try:
        for img in images:
            raw = await img.read()
            data, mime = normalize_image(raw, img.filename or "image")
            content, has_diagram = await extract_from_image(data, mime, provider, model)
            results.append({
                "content": content,
                "has_diagram": has_diagram,
                "image_b64": base64.b64encode(data).decode() if has_diagram else None,
                "image_mime": mime,
            })
    except ExtractionError as e:
        logger.error(
            "Extraction failed for chapter=%r provider=%r model=%r: %s", chapter, provider, model, e.message
        )
        return HTMLResponse(
            _jinja.get_template("upload.html").render(
                error=e.message,
                gemini_models=GEMINI_MODELS,
                selected_provider=provider,
                selected_gemini_model=gemini_model,
            ),
            status_code=502,
        )

    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"results": results, "chapter": chapter.strip()}
    return RedirectResponse(url=f"/pdf/preview/{session_id}", status_code=303)


@router.get("/preview/{session_id}", response_class=HTMLResponse)
async def preview(session_id: str):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    return HTMLResponse(_render(session["results"], session_id, session["chapter"]))


@router.get("/download/{session_id}")
async def download(session_id: str):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    html = _render(session["results"], session_id, session["chapter"])
    pdf_bytes = await generate_pdf(html, _render_header(session["chapter"]))
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=extracted.pdf"},
    )


@router.post("/upload/{session_id}")
async def upload_to_drive(session_id: str):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    html = _render(session["results"], session_id, session["chapter"])
    pdf_bytes = await generate_pdf(html, _render_header(session["chapter"]))
    filename = f"{session['chapter'] or 'extracted'}.pdf"
    try:
        file = await upload_pdf_to_drive(pdf_bytes, filename)
    except Exception as e:
        logger.exception("Drive upload failed for session=%s filename=%r", session_id, filename)
        return JSONResponse(
            status_code=502,
            content={"success": False, "data": None, "message": "Upload failed", "error": str(e)},
        )
    return {
        "success": True,
        "data": {"file_id": file["id"], "web_view_link": file.get("webViewLink")},
        "message": "Uploaded to Drive successfully",
        "error": None,
    }
