#!/usr/bin/env python3
"""
Fathom AI MCP Server
Provides tools for accessing Fathom meeting recordings, transcripts, and summaries.
Requires: FATHOM_API_KEY environment variable

API docs: https://developers.fathom.ai/api-overview
Base URL: https://api.fathom.ai/external/v1
Auth: X-Api-Key header
"""

import os
import json
import sys
import requests
from mcp.server.fastmcp import FastMCP


def _load_api_key() -> str:
    key = os.environ.get("FATHOM_API_KEY", "").strip()
    if key:
        return key
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
    include_action_items: bool = False,
    limit: int = 10,
    created_after: str = None,
    created_before: str = None,
) -> str:
    """
    List the most recent Fathom meetings.

    Args:
        include_transcript: Include full transcript in the response.
        include_summary: Include AI-generated summary (markdown) in the response.
        include_action_items: Include action items with assignees in the response.
        limit: Number of meetings to return (default 10, max 50).
        created_after: ISO timestamp filter, e.g. 2025-01-01T00:00:00Z
        created_before: ISO timestamp filter, e.g. 2025-12-31T23:59:59Z
    """
    params = {"limit": limit}
    if include_transcript:
        params["include_transcript"] = "true"
    if include_summary:
        params["include_summary"] = "true"
    if include_action_items:
        params["include_action_items"] = "true"
    if created_after:
        params["created_after"] = created_after
    if created_before:
        params["created_before"] = created_before

    data = _get("/meetings", params)
    meetings = data.get("items", [])

    if not meetings:
        return "No meetings found."

    results = []
    for m in meetings:
        entry = {
            "recording_id": m.get("recording_id"),
            "title": m.get("title") or "Untitled",
            "created_at": m.get("created_at"),
            "recording_start": m.get("recording_start_time"),
            "recording_end": m.get("recording_end_time"),
            "share_url": m.get("share_url"),
            "participants": [
                inv.get("name") for inv in m.get("calendar_invitees", []) if inv.get("name")
            ],
        }
        if include_summary and m.get("default_summary"):
            entry["summary"] = m["default_summary"].get("markdown_formatted")
        if include_action_items and m.get("action_items"):
            entry["action_items"] = [
                {
                    "description": item.get("description"),
                    "assignee": (item.get("assignee") or {}).get("name"),
                    "timestamp": item.get("recording_timestamp"),
                    "playback_url": item.get("recording_playback_url"),
                }
                for item in m["action_items"]
            ]
        if include_transcript and m.get("transcript"):
            entry["transcript"] = [
                f"[{seg.get('timestamp')}] {seg.get('speaker', {}).get('display_name', 'Unknown')}: {seg.get('text', '').strip()}"
                for seg in m["transcript"]
            ]
        results.append(entry)

    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def get_transcript(recording_id: int) -> str:
    """
    Get the full transcript for a specific recording.
    Returns speaker-labeled segments with HH:MM:SS timestamps.

    Args:
        recording_id: The recording_id from the meeting object (integer).
    """
    data = _get(f"/recordings/{recording_id}/transcript")
    segments = data.get("transcript", [])

    if not segments:
        return "No transcript available for this recording."

    lines = []
    for seg in segments:
        speaker = seg.get("speaker", {}).get("display_name", "Unknown")
        text = seg.get("text", "").strip()
        timestamp = seg.get("timestamp", "")
        lines.append(f"[{timestamp}] {speaker}: {text}")

    return "\n".join(lines)


@mcp.tool()
def get_summary(recording_id: int) -> str:
    """
    Get the AI-generated summary for a meeting recording.

    Args:
        recording_id: The recording_id from the meeting object (integer).
    """
    data = _get(f"/recordings/{recording_id}/summary")
    summary = data.get("summary")
    if not summary:
        return "No summary available for this recording."
    return summary.get("markdown_formatted") or json.dumps(summary, ensure_ascii=False, indent=2)


@mcp.tool()
def get_action_items(recording_id: int) -> str:
    """
    Get action items extracted from a meeting.

    Args:
        recording_id: The recording_id from the meeting object (integer).
    """
    data = _get("/meetings", {"limit": 50, "include_action_items": "true"})
    meetings = data.get("items", [])

    meeting = next((m for m in meetings if m.get("recording_id") == recording_id), None)
    if not meeting:
        return f"Meeting with recording_id {recording_id} not found in recent 50 meetings."

    action_items = meeting.get("action_items") or []
    if not action_items:
        return "No action items found for this meeting."

    lines = []
    for i, item in enumerate(action_items, 1):
        assignee = (item.get("assignee") or {}).get("name", "")
        description = item.get("description", "")
        timestamp = item.get("recording_timestamp", "")
        playback = item.get("recording_playback_url", "")
        line = f"{i}. [{timestamp}] {description}"
        if assignee:
            line += f" (Assignee: {assignee})"
        if playback:
            line += f"\n   Video: {playback}"
        lines.append(line)

    return "\n".join(lines)


@mcp.tool()
def list_teams() -> str:
    """
    List all teams accessible to the authenticated Fathom user.
    """
    data = _get("/teams")
    teams = data.get("items", [])
    if not teams:
        return "No teams found."
    return json.dumps(teams, ensure_ascii=False, indent=2)


@mcp.tool()
def list_team_members(team: str = None) -> str:
    """
    List team members, optionally filtered by team name.

    Args:
        team: Team name to filter by (optional).
    """
    params = {}
    if team:
        params["team"] = team
    data = _get("/team_members", params)
    members = data.get("items", [])
    if not members:
        return "No team members found."
    return json.dumps(members, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: FATHOM_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    mcp.run(transport="stdio")
