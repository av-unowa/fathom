# File Format Reference

## Folder naming

Meeting folders follow the pattern: `YYYY-MM-DD_meeting-slug`

Slugification rules:
- Lowercase everything
- Replace spaces with hyphens
- Remove: `/ \ : * ? " < > | . , ( ) [ ] { } @ # $ % ^ & =`
- Truncate to 60 characters
- Examples:
  - "Product Review Call" → `2026-03-18_product-review-call`
  - "1:1 with Andrii" → `2026-03-15_1-1-with-andrii`
  - "Q1 Planning — Leadership" → `2026-03-10_q1-planning-leadership`

## transcript.md — Full example

```markdown
# Transcript: Product Review Call
**Date:** March 18, 2026 at 14:00
**Duration:** 42 min
**Participants:** Andrii, Maria, John Smith

---

[00:00] Andrii: Let's start with the product updates.
[00:14] Maria: We shipped the new dashboard last week...
[01:02] John Smith: I had a question about the API response times...
```

## summary.md — Full example

```markdown
# Summary: Product Review Call
**Date:** March 18, 2026 at 14:00
**Participants:** Andrii, Maria, John Smith

---

## Overview
The team reviewed the Q1 product roadmap and discussed upcoming API changes.

## Key Points
- Dashboard v2 shipped successfully with positive user feedback
- API latency is above target; investigation needed
- New onboarding flow planned for April release

## Decisions
- Andrii will lead the API performance investigation
- Maria will prepare the April release plan by March 25
```

## tasks.md — Full example

```markdown
# Tasks: Product Review Call
**Date:** March 18, 2026 at 14:00

---

| # | Task | Owner | ClickUp Task ID | Status |
|---|------|-------|-----------------|--------|
| 1 | Investigate API performance issues | Andrii | CU-abc123 | ✅ Created |
| 2 | Prepare April release plan | Maria | CU-abc124 | ✅ Created |
| 3 | Review onboarding flow mockups | John Smith | — | ⚠️ Not found in ClickUp |
```

## Sync state file

Save a `_sync_state.json` in the `fathom-meetings/` root to track which meetings have been synced:

```json
{
  "last_synced": "2026-03-18T15:30:00Z",
  "synced_meeting_ids": [
    "mtg_abc123",
    "mtg_def456"
  ]
}
```

Use this to skip already-synced meetings on subsequent runs.
