import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from app.core.logging import configure_logging
from app.routers import pdf

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Generator")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pdf.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

_jinja = Environment(loader=FileSystemLoader("app/templates"), autoescape=True)


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(_jinja.get_template("upload.html").render())
