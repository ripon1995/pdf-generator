from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from app.routers import pdf

app = FastAPI(title="PDF Generator")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pdf.router)

_jinja = Environment(loader=FileSystemLoader("app/templates"), autoescape=True)


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(_jinja.get_template("upload.html").render())
