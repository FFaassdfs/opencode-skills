# -*- coding: utf-8 -*-
"""
OpenCode server API reusable client.

Usage:
    from opencode_server_client import OpenCodeServerClient, resolve_opencode_cli
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import time
import urllib.request
from typing import Any


def _command_source(command: str) -> str | None:
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"$cmd = Get-Command '{command}' -ErrorAction SilentlyContinue; if ($cmd) {{ $cmd.Source }}",
            ],
            capture_output=True,
            text=True,
            timeout=20,
            encoding="utf-8",
            errors="replace",
        )
        output = result.stdout.strip()
        return output or None
    except Exception:
        return None


def resolve_opencode_cli(extra_candidates: list[str] | None = None) -> str:
    """Resolve OpenCode CLI path with env override + PATH + common locations."""
    candidates = []

    env_cli = os.environ.get("OPENCODE_CLI_PATH")
    if env_cli:
        candidates.append(env_cli)

    for name in ("opencode", "opencode-cli"):
        path = _command_source(name)
        if path:
            candidates.append(path)

    candidates.extend(
        [
            r"D:\opencode\opencode-cli.exe",
            r"D:\opencode\OpenCode.exe",
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Programs", "OpenCode", "opencode-cli.exe"),
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Programs", "OpenCode", "OpenCode.exe"),
        ]
    )

    if extra_candidates:
        candidates.extend(extra_candidates)

    seen = set()
    for candidate in candidates:
        if not candidate:
            continue
        normalized = os.path.normpath(candidate)
        if normalized in seen:
            continue
        seen.add(normalized)
        if os.path.exists(normalized):
            return normalized

    raise FileNotFoundError(
        "Unable to locate OpenCode CLI. Set OPENCODE_CLI_PATH or add opencode/opencode-cli to PATH."
    )


class OpenCodeServerClient:
    def __init__(
        self,
        cli_path: str | None = None,
        server_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        serve_port: int = 4096,
    ) -> None:
        self.cli_path = cli_path or resolve_opencode_cli()
        self.server_url = server_url or os.environ.get("OPENCODE_SERVER_URL", f"http://127.0.0.1:{serve_port}")
        self.username = username or os.environ.get("OPENCODE_SERVER_USERNAME", "opencode")
        self.password = password or os.environ.get("OPENCODE_SERVER_PASSWORD", "")
        self.serve_port = serve_port

    def _headers(self, json_body: bool = False) -> dict[str, str]:
        token = base64.b64encode(f"{self.username}:{self.password}".encode("ascii")).decode("ascii")
        headers = {"Authorization": f"Basic {token}"}
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def request_json(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        body = None
        headers = self._headers(json_body=payload is not None)
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{self.server_url}{path}", data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None

    def ensure_server_running(self, cwd: str | None = None) -> None:
        try:
            self.request_json("GET", "/global/health")
            return
        except Exception:
            pass

        subprocess.Popen(
            [self.cli_path, "serve", "--hostname", "127.0.0.1", "--port", str(self.serve_port)],
            cwd=cwd or os.path.dirname(self.cli_path) or None,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        last_error = None
        for _ in range(30):
            try:
                self.request_json("GET", "/global/health")
                return
            except Exception as exc:
                last_error = exc
                time.sleep(1)

        raise RuntimeError(f"OpenCode server did not become ready: {last_error}")

    def create_session(self, title: str) -> dict[str, Any]:
        session = self.request_json("POST", "/session", {"title": title})
        if not session or "id" not in session:
            raise RuntimeError("Failed to create OpenCode session")
        return session

    def send_message(self, session_id: str, provider_id: str, model_id: str, prompt: str) -> dict[str, Any]:
        response = self.request_json(
            "POST",
            f"/session/{session_id}/message",
            {
                "model": {"providerID": provider_id, "modelID": model_id},
                "parts": [{"type": "text", "text": prompt}],
            },
        )
        if not response:
            raise RuntimeError("OpenCode message endpoint returned no data")
        return response

    @staticmethod
    def extract_text(parts: list[dict[str, Any]]) -> str:
        texts = []
        for part in parts:
            if part.get("type") == "text" and part.get("text"):
                texts.append(str(part["text"]).strip())
        return "\n".join(text for text in texts if text).strip()
