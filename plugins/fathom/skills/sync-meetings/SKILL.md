---
name: sync-meetings
description: >
  Use this skill when the user asks to "sync meetings", "save meetings locally",
  "save calls", "create tasks from meetings", "update ClickUp from Fathom",
  "save transcripts", "sync Fathom to ClickUp", "what tasks came out of my calls",
  "зберегти дзвінки", "синхронізувати зустрічі", "задачі з дзвінків",
  or anything related to saving Fathom meeting data locally and creating tasks in ClickUp.
metadata:
  version: "0.1.0"
---

## Sync Fathom Meetings → Local Files + ClickUp Tasks

This skill saves meeting data locally as structured Markdown files and creates ClickUp tasks from action items, assigned to the right participants.

---

### Step 1 — Ask the user where to save files

If a directory is not already available (no folder selected), use `request_cowork_directory` to ask the user to select a folder. All meeting files will be saved there.

Suggested subfolder structure inside the selected folder:
```
fathom-meetings/
  YYYY-MM-DD_meeting-title/
    transcript.md
    summary.md
    tasks.md
```

Create the `fathom-meetings/` root folder if it doesn't exist.

---

### Step 2 — Fetch meetings from Fathom

Call `list_meetings(include_transcript=true, include_summary=true, limit=20)`.

For each meeting, build a safe folder name:
- Format: `YYYY-MM-DD_slug` where slug is the meeting title lowercased, spaces replaced with hyphens, special chars removed
- Example: `2026-03-18_product-review-call`

Skip meetings whose folder already exists (already synced). Ask the user if they want to re-sync all or only new ones.

---

### Step 3 — Save local files per meeting

For each meeting, create three files:

**transcript.md**
```markdown
# Transcript: {meeting title}
**Date:** {readable date and time}
**Duration:** {X} min
**Participants:** {comma-separated names}

---

[00:00] Speaker Name: text...
[01:23] Other Speaker: text...
```

**summary.md**
```markdown
# Summary: {meeting title}
**Date:** {readable date and time}
**Participants:** {comma-separated names}

---

## Overview
{summary text}

## Key Points
{key points if available}

## Decisions
{decisions if available}
```

**tasks.md**
```markdown
# Tasks: {meeting title}
**Date:** {readable date and time}

---

| # | Task | Owner | ClickUp Status |
|---|------|-------|---------------|
| 1 | Do X | Alice | ✅ Created |
| 2 | Do Y | Bob   | ⚠️ Not found in ClickUp |
```

After writing files, tell the user how many meetings were saved.

---

### Step 4 — Resolve ClickUp members

For each unique participant name in the meetings, call `clickup_find_member_by_name` or `clickup_get_workspace_members` to find their ClickUp user ID.

Build a mapping: `{ "Fathom participant name" → ClickUp user ID }`.

If a participant cannot be found in ClickUp:
- Skip assigning them, but still create the task unassigned
- Note this in the tasks.md file as "⚠️ Not found in ClickUp"

---

### Step 5 — Determine ClickUp list for tasks

Before creating tasks, determine where to put them:
- Call `clickup_get_workspace_hierarchy` to find available lists
- Ask the user which list (or folder/space) tasks should go into
- Remember their choice for the rest of the sync

---

### Step 6 — Create ClickUp tasks from action items

For each meeting, iterate over action items from the summary.

For each action item:
1. Determine the owner — use the `owner` field from the action item if present; otherwise leave unassigned
2. Look up the owner's ClickUp user ID from the mapping built in Step 4
3. Call `clickup_create_task` with:
   - `name`: the action item text
   - `description`: "From Fathom meeting: {meeting title} on {date}\n\nTranscript folder: {local path}"
   - `assignees`: [ClickUp user ID] if found, otherwise empty
   - `due_date`: omit unless the action item mentions a specific date
4. Record the created task ID in tasks.md

If there are no action items in a meeting's summary, note this in tasks.md: "No action items found."

---

### Step 7 — Final report

After completing the sync, present a summary to the user:

```
✅ Sync complete

📁 Meetings saved: X
🗂️ Files created: X (transcripts, summaries, tasks)
✅ ClickUp tasks created: X
⚠️ Participants not matched in ClickUp: [names]
```

Offer to open the saved folder or review any specific meeting.

---

### Important Rules

- Always use the `FATHOM_API_KEY` via the Fathom MCP tools — never call the API directly
- Do not overwrite existing meeting files unless the user explicitly asks to re-sync
- When creating ClickUp tasks, add a tag `fathom` to all tasks so they can be filtered
- If a meeting has no summary yet (processing in progress), save the transcript only and skip ClickUp task creation for that meeting — note it for the user
- Prefer the participant's display name when matching to ClickUp; try partial name match if exact match fails
