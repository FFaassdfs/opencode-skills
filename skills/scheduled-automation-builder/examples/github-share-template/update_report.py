# -*- coding: utf-8 -*-
"""
Replace this file with real data fetching logic.
This sample writes demo JSON and HTML so the automation flow can be tested.
"""

import json
from datetime import datetime


def main() -> None:
    data = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": [
            {"name": "Sample A", "value": 123, "change": 1.2},
            {"name": "Sample B", "value": 456, "change": -0.8},
        ],
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    html = f"""<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Scheduled Report</title>
</head>
<body>
  <div class=\"container\">
    <h1>Scheduled Report</h1>
    <p>Updated: {data['updated_at']}</p>
    <div class=\"footer\">Base report generated.</div>
  </div>
</body>
</html>"""

    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
