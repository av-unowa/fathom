# Fathom Plugin

Access your Fathom AI meeting recordings, transcripts, summaries, and action items directly in Claude.

## Components

| Component  | Name          | Purpose                                                        |
|------------|---------------|----------------------------------------------------------------|
| MCP Server | fathom        | Connects to the Fathom API via your API key                    |
| Skill      | fathom        | Guides Claude on how to use Fathom data                        |
| Skill      | sync-meetings | Saves meetings locally + creates ClickUp tasks from action items |

## Setup

This plugin requires a **Fathom API key** set as an environment variable:

```
FATHOM_API_KEY=your_api_key_here
```

Generate your API key at: https://app.fathom.video/settings/developer

### Dependencies

The MCP server requires Python 3.9+ with:

```bash
pip install mcp requests
```

## Available Tools

| Tool              | Description                                          |
|-------------------|------------------------------------------------------|
| `list_meetings`   | List recent meetings with optional transcripts       |
| `get_meeting`     | Get details for a specific meeting                   |
| `get_transcript`  | Get full timestamped transcript for a recording      |
| `get_summary`     | Get AI-generated summary for a meeting               |
| `get_action_items`| Get action items extracted from a meeting            |

## Usage

Once installed, just ask Claude naturally:

- "Show my recent Fathom meetings"
- "Get the transcript from my last meeting"
- "What were the action items from yesterday's call?"
- "Summarize my meeting with [person]"
- "Sync my Fathom meetings" — saves all calls locally as files + creates ClickUp tasks
- "Save meetings locally" — downloads transcripts and summaries as Markdown files
- "Create tasks from my calls" — extracts action items and pushes them to ClickUp

## Rate Limits

Fathom API allows up to 60 requests per minute per user.
