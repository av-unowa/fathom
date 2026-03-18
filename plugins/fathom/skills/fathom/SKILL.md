---
name: fathom
description: >
  Use this skill when the user asks to "show my meetings", "get transcript",
  "summarize a meeting", "what was discussed", "show action items from a call",
  "get Fathom recordings", or anything related to accessing Fathom AI meeting data.
metadata:
  version: "0.1.0"
---

## Working with Fathom Meetings

Use the available Fathom MCP tools to retrieve and present meeting data.

### Tools Available

- `list_meetings` — list recent meetings; use `include_transcript=true` or `include_summary=true` to fetch content inline
- `get_meeting` — fetch metadata for a specific meeting by ID
- `get_transcript` — fetch the full, timestamped, speaker-labeled transcript for a recording
- `get_summary` — fetch the AI-generated summary for a meeting
- `get_action_items` — fetch action items from a meeting's summary

### Common Workflows

**User asks to see recent meetings:**
Call `list_meetings` with default parameters. Present results as a readable list with title, date, duration, and participants.

**User asks for a transcript:**
1. If no meeting ID is given, call `list_meetings` first and ask the user to pick one.
2. Call `get_transcript(recording_id)` using the recording ID from the meeting object.
3. Present the transcript in a clean, readable format grouped by speaker.

**User asks for a summary or action items:**
Call `get_summary` or `get_action_items` with the meeting ID. If the user hasn't specified which meeting, show the recent list first.

**User asks "what was decided in our last meeting":**
Call `list_meetings(include_summary=true, limit=1)` and present the summary and action items from the most recent meeting.

### Presentation Guidelines

- Format transcripts as `[MM:SS] Speaker: text` blocks
- Group action items as a numbered list with owner if available
- When listing meetings, always show: title, date, duration, and participant names
- If a meeting has no title, display it as "Untitled Meeting"
- Dates are in ISO format — convert to readable format (e.g., "March 15, 2026 at 14:30")
