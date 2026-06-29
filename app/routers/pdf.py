import base64
import io
import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from app.services.extraction import extract_from_image
from app.services.pdf_generator import generate_pdf

router = APIRouter(prefix="/pdf", tags=["pdf"])

_jinja = Environment(loader=FileSystemLoader("app/templates"), autoescape=True)

_sessions: dict[str, list[dict]] = {}


def _render(results: list[dict], session_id: str) -> str:
    return _jinja.get_template("preview.html").render(
        results=results,
        session_id=session_id,
    )


@router.post("/generate")
async def generate(images: list[UploadFile] = File(...)):
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
    _sessions[session_id] = results
    return RedirectResponse(url=f"/pdf/preview/{session_id}", status_code=303)


@router.get("/preview/{session_id}", response_class=HTMLResponse)
async def preview(session_id: str):
    results = _sessions.get(session_id)
    if not results:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    return HTMLResponse(_render(results, session_id))


@router.get("/download/{session_id}")
async def download(session_id: str):
    results = _sessions.get(session_id)
    if not results:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    html = _render(results, session_id)
    pdf_bytes = await generate_pdf(html)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=extracted.pdf"},
    )
