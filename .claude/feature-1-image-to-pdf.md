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

- Every page must have a margin; the **margin color is blue** on all pages.
- Inside the top margin of every page, show the **NumberNest logo** (black "Number" + black square-root icon + yellow "Nest", with tagline).
  - Asset: `app/static/logo.svg`. Inlined into `preview.html` server-side (via `logo_svg` template var in `app/routers/pdf.py`) rather than linked, since Playwright's `page.set_content()` has no page origin to resolve a relative `<img src>` against.
- Each page should include a subtle **mathematical watermark** in the background (e.g. faint math symbols/equations), since generated PDFs are predominantly mathematical content. Watermark must not obscure or interfere with readability of the extracted content.

## Notes

- Math rendering in the output PDF must support LaTeX (e.g. via WeasyPrint + MathJax, ReportLab, or a LaTeX compiler)
- Diagram extraction may require a separate vision/detection step distinct from text/math extraction