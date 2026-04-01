import argparse
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def export_via_playwright(html_path: Path, pdf_path: Path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 2000}, device_scale_factor=1.5)
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(5000)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            display_header_footer=False,
            margin={"top": "10mm", "bottom": "10mm", "left": "8mm", "right": "8mm"},
            prefer_css_page_size=True,
        )
        browser.close()


def export_via_screenshot(html_path: Path, pdf_path: Path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 1600}, device_scale_factor=2)
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(5000)
        png_bytes = page.screenshot(full_page=True, type="png")
        browser.close()

    image = Image.open(BytesIO(png_bytes)).convert("RGB")
    img_width, img_height = image.size
    page_width, page_height = A4
    margin = 18
    usable_width = page_width - margin * 2
    usable_height = page_height - margin * 2
    scale = usable_width / img_width
    slice_height_px = int(usable_height / scale)

    pdf = canvas.Canvas(str(pdf_path), pagesize=A4)
    top = page_height - margin
    y = 0
    while y < img_height:
        lower = min(y + slice_height_px, img_height)
        crop = image.crop((0, y, img_width, lower))
        temp = BytesIO()
        crop.save(temp, format="PNG")
        temp.seek(0)
        draw_height = (lower - y) * scale
        pdf.drawInlineImage(Image.open(temp), margin, top - draw_height, width=usable_width, height=draw_height)
        pdf.showPage()
        y = lower
    pdf.save()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("html_path")
    parser.add_argument("pdf_path")
    parser.add_argument("--mode", choices=["playwright", "screenshot"], default="playwright")
    args = parser.parse_args()

    html_path = Path(args.html_path)
    pdf_path = Path(args.pdf_path)

    if args.mode == "playwright":
        export_via_playwright(html_path, pdf_path)
    else:
        export_via_screenshot(html_path, pdf_path)

    print(str(pdf_path))


if __name__ == "__main__":
    main()
