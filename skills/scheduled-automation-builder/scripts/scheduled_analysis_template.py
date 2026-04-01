# -*- coding: utf-8 -*-
"""
Reusable scheduled analysis template.

Intended as a starting point for tasks like:
- update data -> call OpenCode model -> update HTML / Markdown / JSON
- daily report generation
- post-market commentary generation
"""

from __future__ import annotations

import html
import json
import os
from datetime import datetime
from typing import Any

from opencode_server_client import OpenCodeServerClient  # type: ignore[import-not-found]


WORK_DIR = os.environ.get("AUTOMATION_WORK_DIR", os.getcwd())
INPUT_JSON = os.environ.get("AUTOMATION_INPUT_JSON", os.path.join(WORK_DIR, "data.json"))
OUTPUT_HTML = os.environ.get("AUTOMATION_OUTPUT_HTML", os.path.join(WORK_DIR, "report.html"))
HISTORY_JSON = os.environ.get("AUTOMATION_HISTORY_JSON", os.path.join(WORK_DIR, "data_old.json"))

MODEL_PROVIDER = os.environ.get("AUTOMATION_MODEL_PROVIDER", "opencode")
MODEL_ID = os.environ.get("AUTOMATION_MODEL_ID", "big-pickle")


def load_json(path: str) -> Any:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_prompt(today_data: Any, yesterday_data: Any | None = None) -> str:
    prompt = "请根据以下数据生成简洁专业的自动化点评。\n\n"
    prompt += f"今日数据：\n{json.dumps(today_data, ensure_ascii=False, indent=2)}\n"
    if yesterday_data is not None:
        prompt += f"\n昨日数据：\n{json.dumps(yesterday_data, ensure_ascii=False, indent=2)}\n"
    prompt += "\n请给出整体概述、关键变化、后续观察点和简短建议。"
    return prompt


def inject_analysis_into_html(html_path: str, analysis_text: str) -> None:
    with open(html_path, "r", encoding="utf-8") as f:
        html_text = f.read()

    marker = '<div class="footer">'
    if marker not in html_text:
        raise RuntimeError("HTML footer marker not found")

    card = (
        '        <div class="card analysis-card">\n'
        '            <div class="card-header">\n'
        '                <span class="card-title">AI Analysis</span>\n'
        '            </div>\n'
        '            <div class="analysis-content">\n'
        f'                <pre style="white-space: pre-wrap; line-height: 1.8;">{html.escape(analysis_text)}</pre>\n'
        '            </div>\n'
        '        </div>\n'
    )
    footer = (
        '        <div class="footer">\n'
        f'            Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        '        </div>\n'
        '    </div>\n'
        '</body>\n'
        '</html>'
    )

    html_text = html_text.split(marker)[0] + card + footer

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_text)


def main() -> None:
    today_data = load_json(INPUT_JSON)
    if not today_data:
        raise RuntimeError(f"Input data not found: {INPUT_JSON}")

    yesterday_data = load_json(HISTORY_JSON)
    prompt = build_prompt(today_data, yesterday_data)

    client = OpenCodeServerClient()
    client.ensure_server_running()
    session = client.create_session("Scheduled automation analysis")
    response = client.send_message(session["id"], MODEL_PROVIDER, MODEL_ID, prompt)
    analysis_text = client.extract_text(response.get("parts", []))
    if not analysis_text:
        raise RuntimeError("Model returned empty analysis")

    inject_analysis_into_html(OUTPUT_HTML, analysis_text)
    save_json(HISTORY_JSON, today_data)


if __name__ == "__main__":
    main()
