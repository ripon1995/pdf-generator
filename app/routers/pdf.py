import base64
import io
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from app.services.content_formatting import format_content
from app.services.extraction import extract_from_image
from app.services.pdf_generator import generate_pdf

router = APIRouter(prefix="/pdf", tags=["pdf"])

_jinja = Environment(loader=FileSystemLoader("app/templates"), autoescape=True)

_sessions: dict[str, dict] = {}

# Inlined (not linked/referenced by <img src>) so Playwright's page.set_content() —
# which has no page origin to resolve a relative URL against — still renders styled output.
_CSS = Path("app/static/styles.css").read_text()
_LOGO_SVG = Path("app/static/logo.svg").read_text()


def _render(results: list[dict], session_id: str, chapter: str) -> str:
    formatted = [{**r, "content": format_content(r["content"])} for r in results]
    return _jinja.get_template("preview.html").render(
        results=formatted,
        session_id=session_id,
        inline_css=_CSS,
        logo_svg=_LOGO_SVG,
        chapter=chapter,
    )


@router.post("/generate")
async def generate(images: list[UploadFile] = File(...), chapter: str = Form(...)):
    if not images:
        raise HTTPException(status_code=400, detail="No images provided.")

    results = []
    for img in images:
        data = await img.read()
        mime = img.content_type or "image/jpeg"
        content, has_diagram = await extract_from_image(data, mime)
        results.append({
            "content": content,
            "has_diagram": has_diagram,
            "image_b64": base64.b64encode(data).decode() if has_diagram else None,
            "image_mime": mime,
        })

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
    pdf_bytes = await generate_pdf(html)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=extracted.pdf"},
    )
