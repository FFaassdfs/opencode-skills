# -*- coding: utf-8 -*-
"""
Minimal example of scheduled analysis using the bundled reusable template.
Copy the reusable scripts into your project or import them from the skill bundle.
"""

import json
import os
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_SCRIPTS = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "..", "scripts")
)
sys.path.insert(0, SKILL_SCRIPTS)

from scheduled_analysis_template import main  # type: ignore[import-not-found]  # noqa: E402


if __name__ == "__main__":
    os.environ.setdefault("AUTOMATION_WORK_DIR", SCRIPT_DIR)
    os.environ.setdefault("AUTOMATION_INPUT_JSON", os.path.join(SCRIPT_DIR, "data.json"))
    os.environ.setdefault("AUTOMATION_OUTPUT_HTML", os.path.join(SCRIPT_DIR, "report.html"))
    os.environ.setdefault("AUTOMATION_HISTORY_JSON", os.path.join(SCRIPT_DIR, "data_old.json"))
    main()
