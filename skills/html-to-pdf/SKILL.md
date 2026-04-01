---
name: html-to-pdf
description: Use when the user wants to convert local HTML files into PDF files, especially for report delivery, offline archiving, printable exports, or when browser print output is broken. Also use when HTML contains ECharts, dynamic charts, or long report pages that need reliable rendering without browser header/footer pollution.
---

# HTML to PDF

## Overview

This skill converts local HTML reports into clean PDF files.

The default path is Playwright `page.pdf()` because it renders modern HTML/CSS/JS well and usually preserves charts.
If browser-based PDF export still injects unwanted headers, footers, timestamps, or `file:///` URLs, fall back to full-page screenshot capture plus image-sliced PDF generation.

## When to Use

- User asks to convert one or more `.html` files to `.pdf`
- Report HTML contains ECharts, charts, or client-side rendering that needs time to finish
- Browser print output is abnormal: blank pages, header/footer noise, timestamps, `file:///` path, broken pagination
- User needs a printable/offline deliverable from an existing HTML artifact

Do not use this skill for creating a PDF from scratch when there is no HTML source. In that case use a PDF creation skill instead.

## Workflow

1. Identify the input HTML file paths and target PDF paths.
2. Prefer Playwright export first.
3. Wait for page render to finish before exporting.
4. Verify the PDF is non-empty and readable.
5. If the PDF still contains browser print pollution or render defects, switch to screenshot-based export.

## Preferred Method

Use the bundled script:

```bash
python "C:\Users\veken\.opencode\skills\html-to-pdf\scripts\export_html_to_pdf.py" "input.html" "output.pdf"
```

For multiple files, run it once per file.

## Fallback Rule

If the generated PDF shows any of the following, rerun with screenshot mode:

- timestamp in header/footer
- `file:///` path printed on page
- page number injected by browser print engine
- charts missing because page rendered too early
- blank or partially rendered sections

Use:

```bash
python "C:\Users\veken\.opencode\skills\html-to-pdf\scripts\export_html_to_pdf.py" "input.html" "output.pdf" --mode screenshot
```

## Verification

After export, verify at least one of these:

- file exists and size is reasonable
- page count is non-zero
- extracted text does not contain obvious browser-print junk like `file:///`
- charts and layout visually appear in the PDF

If text extraction still shows browser-print noise, do not assume the PDF is acceptable. Re-export using screenshot mode.

## Troubleshooting

### Symptom: PDF contains `file:///`, timestamps, or browser page numbers

Cause: the browser print engine injected default header/footer content.

Action:

- First avoid raw browser `--print-to-pdf` CLI flows for local `file://` pages when quality matters.
- Prefer Playwright export through the bundled script.
- If the PDF still shows browser print pollution, switch to `--mode screenshot`.

### Symptom: ECharts or dynamic widgets are blank or incomplete

Cause: the page exported before client-side rendering finished.

Action:

- Wait for `networkidle`
- Add an explicit render wait before export
- Re-run with screenshot mode if chart rendering remains unstable

### Symptom: PDF layout is correct on screen but broken after print

Cause: print layout and screen layout differ, especially for long dashboards and absolute-positioned charts.

Action:

- Prefer screenshot mode for visually exact delivery
- Use Playwright mode when selectable text matters more than exact visual fidelity

### Symptom: Chinese report PDF looks garbled in extracted text

Cause: PDF text extraction can be imperfect even when visual rendering is correct.

Action:

- Judge the PDF visually first
- If visual output is correct, this is not necessarily a rendering failure
- Only treat it as a blocker when the visible PDF itself is broken

## Notes

- Playwright export preserves selectable text better.
- Screenshot fallback is more robust for visual fidelity and avoids browser header/footer pollution, but resulting PDFs behave more like image pages.
- For Chinese report HTML, make sure the HTML itself already renders correctly before converting.
- For delivery-grade client reports, screenshot mode is often the safer final fallback.
