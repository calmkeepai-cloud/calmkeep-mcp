import os
import sys
import json
import uuid
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calmkeep")

CALMKEEP_URL = os.environ.get(""https://diargallop--calmkeep-service-calmkeep-service.modal.run")
CALMKEEP_API_KEY = os.environ.get("CALMKEEP_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# ---------------------------------------------------------
# Persistent session storage for MCP process
# ---------------------------------------------------------

_ACTIVE_SESSION_ID: str | None = None


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


@mcp.tool()
def calmkeep_chat(
    prompt: str,
    session_id: str | None = None,
    max_tokens: int = 4000,
    enable_scope_lock: bool = True,
    phase_hint: str | None = None,
) -> str:
    global _ACTIVE_SESSION_ID

    try:
        log(f"[calmkeep] prompt={prompt!r}")

        if not CALMKEEP_URL:
            return "Error: CALMKEEP_URL is not set."
        if not CALMKEEP_API_KEY:
            return "Error: CALMKEEP_API_KEY is not set."
        if not ANTHROPIC_API_KEY:
            return "Error: ANTHROPIC_API_KEY is not set."
        if not prompt or not prompt.strip():
            return "Error: prompt is required."

        # ---------------------------------------------------------
        # Session handling
        # ---------------------------------------------------------

        if session_id:
            _ACTIVE_SESSION_ID = session_id
        elif not _ACTIVE_SESSION_ID:
            _ACTIVE_SESSION_ID = str(uuid.uuid4())

        session_id = _ACTIVE_SESSION_ID

        url = CALMKEEP_URL.rstrip("/") + "/runtime"

        params = {
            "max_tokens": max_tokens,
            "enable_scope_lock": enable_scope_lock,
            "session_id": session_id,
        }

        if phase_hint:
            params["phase_hint"] = phase_hint

        payload = {
            "prompt": prompt,
            "params": params
        }

        headers = {
            "calmkeep-key": CALMKEEP_API_KEY,
            "anthropic-api-key": ANTHROPIC_API_KEY,
            "Content-Type": "application/json",
        }

        response = httpx.post(url, json=payload, headers=headers, timeout=120.0)
        response.raise_for_status()

        data = response.json()

        text = data.get("result", {}).get("text")

        log(f"[calmkeep] session_id={session_id}")
        log(f"[calmkeep] response_text={text!r}")
        log(f"[calmkeep] raw={json.dumps(data)[:2000]}")

        if not data.get("ok", False):
            return f"Runtime error: {data}"

        if text is None or not str(text).strip():
            return "(Empty text returned by Calmkeep.)"

        return str(text)

    except httpx.HTTPStatusError as e:
        log(f"[calmkeep] HTTP {e.response.status_code}: {e.response.text}")
        return f"HTTP error {e.response.status_code}: {e.response.text}"

    except Exception as e:
        log(f"[calmkeep] Exception: {repr(e)}")
        return f"Error connecting to Calmkeep: {str(e)}"


if __name__ == "__main__":
    mcp.run()
