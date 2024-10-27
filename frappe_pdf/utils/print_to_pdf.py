import asyncio
import tempfile

import frappe
from pyppeteer import launch


async def _print_to_pdf(html, options):
    browser = await launch(
        headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False
    )
    try:
        page = await browser.newPage()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=f"{frappe.generate_hash()}.html", delete=True
        ) as html_file:
            html_file.write(html)
            html_file.seek(0)

            await page.goto(f"file:///{html_file.name}")

        pdf_options = {
            "printBackground": True,
            "preferCSSPageSize": True,
        }

        if options:
            options["width"] = options.get("page-width") or options.get("width")
            options["height"] = options.get("page-height") or options.get("height")

            for key in ("width", "height"):
                if options.get(key):
                    pdf_options[key] = options.get(key)

            margin = {}
            for key in (
                "top",
                "bottom",
                "left",
                "right",
            ):
                if options.get(f"margin-{key}"):
                    margin[key] = options.get(f"margin-{key}")

            if margin:
                pdf_options["margin"] = margin

        output = await page.pdf(pdf_options)
        await browser.close()

        return output

    except Exception as e:
        await browser.close()
        raise e


def print_to_pdf(html, options):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    return asyncio.get_event_loop().run_until_complete(_print_to_pdf(html, options))
