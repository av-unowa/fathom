#!/usr/bin/env python3
"""
Fathom AI MCP Server
Provides tools for accessing Fathom meeting recordings, transcripts, and summaries.
Requires: FATHOM_API_KEY environment variable
"""

import os
import json
import sys
import requests
from mcp.server.fastmcp import FastMCP

def _load_api_key() -> str:
    # 1. Try environment variable
    key = os.environ.get("FATHOM_API_KEY", "").strip()
    if key:
        return key
    # 2. Fallback: read from ~/.zshenv
    for path in [os.path.expanduser("~/.zshenv"), os.path.expanduser("~/.zshrc")]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("export FATHOM_API_KEY="):
                        return line.split("=", 1)[1].strip().strip("'\"")
    return ""

API_KEY = _load_api_key()
BASE_URL = "https://api.fathom.ai/external/v1"

mcp = FastMCP("fathom")


def _headers():
    return {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json",
    }


def _get(path: str, params: dict = None) -> dict:
    url = f"{BASE_URL}{path}"
    resp = requests.get(url, headers=_headers(), params=params or {}, timeout=30)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def list_meetings(
    include_transcript: bool = False,
    include_summary: bool = False,
    limit: int = 10,
) -> str:
    """
    List the most recent Fathom meetings.

    Args:
        include_transcript: Include full transcript text in the response.
        include_summary: Include AI-generated summary in the response.
        limit: Number of meetings to return (default 10, max 50).
    """
    params = {"limit": limit}
    if include_transcript:
        params["include_transcript"] = "true"
    if include_summary:
        params["include_summary"] = "true"

    data = _get("/meetings", params)
    meetings = data.get("meetings", [])

    if not meetings:
        return "No meetings found."

    results = []
    for m in meetings:
        entry = {
            "id": m.get("id"),
            "title": m.get("title") or "Untitled",
            "date": m.get("started_at"),
            "duration_min": round(m.get("duration_seconds", 0) / 60, 1),
            "participants": [p.get("name") for p in m.get("participants", [])],
        }
        if include_summary and m.get("summary"):
            entry["summary"] = m["summary"]
        if include_transcript and m.get("transcript"):
            entry["transcript"] = m["transcript"]
        results.append(entry)

    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def get_meeting(meeting_id: str) -> str:
    """
    Get detailed information about a specific meeting by its ID.

    Args:
        meeting_id: The Fathom meeting ID.
    """
    data = _get(f"/meetings/{meeting_id}")
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def get_transcript(recording_id: str) -> str:
    """
    Get the full transcript for a specific recording.
    Returns speaker-labeled, timestamped segments.

    Args:
        recording_id: The recording ID from the meeting object.
    """
    data = _get(f"/recordings/{recording_id}/transcript")
    segments = data.get("segments", [])

    if not segments:
        return "No transcript available for this recording."

    lines = []
    for seg in segments:
        speaker = seg.get("speaker_name", "Unknown")
        text = seg.get("text", "").strip()
        time_ms = seg.get("start_time_ms", 0)
        mins = time_ms // 60000
        secs = (time_ms % 60000) // 1000
        lines.append(f"[{mins:02d}:{secs:02d}] {speaker}: {text}")

    return "\n".join(lines)


@mcp.tool()
def get_summary(meeting_id: str) -> str:
    """
    Get the AI-generated summary and action items for a meeting.

    Args:
        meeting_id: The Fathom meeting ID.
    """
    data = _get(f"/meetings/{meeting_id}", params={"include_summary": "true"})
    summary = data.get("summary")
    if not summary:
        return "No summary available for this meeting."
    return json.dumps(summary, ensure_ascii=False, indent=2)


@mcp.tool()
def get_action_items(meeting_id: str) -> str:
    """
    Get the action items extracted from a meeting.

    Args:
        meeting_id: The Fathom meeting ID.
    """
    data = _get(f"/meetings/{meeting_id}", params={"include_summary": "true"})
    summary = data.get("summary", {})
    action_items = summary.get("action_items", [])

    if not action_items:
        return "No action items found for this meeting."

    lines = []
    for i, item in enumerate(action_items, 1):
        owner = item.get("owner", "")
        text = item.get("text", item) if isinstance(item, dict) else str(item)
        lines.append(f"{i}. {text}" + (f" (Owner: {owner})" if owner else ""))

    return "\n".join(lines)


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: FATHOM_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    mcp.run(transport="stdio")
