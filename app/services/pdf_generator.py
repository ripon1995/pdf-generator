from playwright.async_api import async_playwright

# Reserves room at the top of every physical PDF page for header_template — sized to
# fit its 20mm lead-in + header row + rule lines (see app/templates/pdf_header.html).
_HEADER_MARGIN_TOP = "52mm"


async def generate_pdf(html_content: str, header_html: str | None = None) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        await page.evaluate(
            "typeof MathJax !== 'undefined' ? MathJax.startup.promise : Promise.resolve()"
        )
        if header_html is not None:
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                display_header_footer=True,
                header_template=header_html,
                footer_template="<span></span>",
                margin={"top": _HEADER_MARGIN_TOP, "bottom": "0mm", "left": "0mm", "right": "0mm"},
            )
        else:
            pdf_bytes = await page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
            )
        await browser.close()
        return pdf_bytes
