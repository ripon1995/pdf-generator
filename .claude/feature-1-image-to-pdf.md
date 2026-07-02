# Feature 1: Image to PDF

## Overview

Accept one or more images as input, extract all content, and generate a structured PDF.

## Requirements

- **Mathematical content** — extract math expressions and preserve proper formatting (e.g. LaTeX), not plain text approximations
- **Diagrams** — detect and extract diagrams/figures from images and include them in the output PDF
- **PDF output** — assemble extracted text, math, and diagrams into a well-structured PDF

## Input / Output

- **Input:** one or more image files (JPEG, PNG, etc.)
- **Output:** a single A4-size, print-ready PDF containing the extracted and formatted content

## Preview Before Download

Before the PDF is downloaded, the user should be shown a preview of the generated content. The download is only triggered after the user confirms from the preview.

## PDF Specifications

- Page size: **A4** (210 × 297 mm)
- Must be print-ready (correct margins, no content clipping)

## Branding & Page Styling

Reference: `app/static/Exercise 10.4 - Integration Document.pdf` — a plain, print-clean document style (no colored margin, no watermark). Superseded an earlier heavier-branded design (colored margin band/border, per-page watermark, per-page logo corner mark) in favor of matching this reference.

- Plain white pages, standard **20mm margin** on all sides (`.page-inner` padding). No colored border, no background watermark.
- The **NumberNest logo** (`app/static/logo.svg`, inlined per `logo_svg` in `app/routers/pdf.py`) appears once, as a document header at the top of **page 1 only** — right-aligned, ~14mm tall, followed by a double rule (2px + 1px, `#001A40`) separating it from the content. Not repeated on subsequent pages.
- No browser-style print chrome (date/title header, file-path/page-number footer) — that's an artifact of how the reference PDF happened to be produced (browser "Print to PDF"), not an intentional design element.

## Notes

- Math rendering in the output PDF must support LaTeX (e.g. via WeasyPrint + MathJax, ReportLab, or a LaTeX compiler)
- Diagram extraction may require a separate vision/detection step distinct from text/math extraction