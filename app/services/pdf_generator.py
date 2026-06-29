from playwright.async_api import async_playwright


async def generate_pdf(html_content: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        await page.evaluate(
            "typeof MathJax !== 'undefined' ? MathJax.startup.promise : Promise.resolve()"
        )
        pdf_bytes = await page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"},
        )
        await browser.close()
        return pdf_bytes
