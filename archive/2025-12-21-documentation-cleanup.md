# Documentation Cleanup & Consistency Fixes

**Date:** 2025-12-21

## Changes Applied

### 1. ✅ Chief of Stuff (Lean into the pun)
- Updated README.md: "Chief of Staff" → "Chief of Stuff"
- Updated .cursorrules: "Chief of Staff App" → "Chief of Stuff"
- Repo name already correct: `chief-of-stuff`

### 2. ✅ Removed Hours/Week Commitments
- Removed from `clients/nedl/README.md` (was "5-15 hours/week")
- Removed from `clients/nextitle/README.md` (was "~10 hours/week")
- Updated `clients/INDEX.md`: "~20 hrs/week total" → "variable hours"
- **Rationale:** No commitments made; avoid false expectations

### 3. ✅ Clarified Billing Ritual
- SCHEDULE.md: "prepare for invoicing" → "verify hours logged"
- TIME.md: "Submit hours weekly/monthly" → "Track hours, invoice as requested"
- Merged SCHEDULE.md sections: "Recurring Meetings" + "Weekly Reminders" → "Recurring"
- **Rationale:** Hours tracking is a personal ritual, not a client deadline

### 4. ✅ Added Projects Pattern to Navigate
- Updated README.md and .cursorrules Navigate section
- Added: `projects/<project>.md` → project details
- Matches pattern already established for clients

### 5. ✅ Added Tag Search Command
- Added to README.md commands: `search raw: [tag]`
- Added to .cursorrules commands with conventions
- Documented tag conventions in .cursorrules rules section
- **Convention:** kebab-case, lowercase (e.g., `entity-resolution`, `data-quality`)

### 6. ✅ Aligned Dev Workspace Language
- Updated .cursorrules dev work rule
- Added detail: "(testing, experiments, notebooks, prototypes)"
- Matches README.md description

### 7. ✅ NexTitle Capitalization Convention
- Added to .cursorrules: "NexTitle (capital T) in prose, `nextitle` (lowercase) in file paths/slugs"
- Already mostly correct in existing files

### 8. ✅ Merged SCHEDULE.md Sections
- Combined "Recurring Meetings" and "Weekly Reminders" into unified "Recurring" table
- Clearer structure: Frequency | Task | Client

### 9. 🔄 Archive Pattern (DEFERRED)
- Issue: Need way to track completed accomplishments for client comms
- Current: "Recently Completed" sections create noise in project files
- Desired: True SCD Type 1 in projects/, archive pattern for history
- **Next:** Design archive/accomplishments/ pattern before implementing

## Files Modified

1. `.cursorrules` - Title, navigate, commands, rules
2. `README.md` - Title, navigate, commands
3. `clients/INDEX.md` - Removed hours commitment
4. `clients/nedl/README.md` - Removed hours section
5. `clients/nextitle/README.md` - Removed hours section
6. `TIME.md` - Updated billing notes
7. `SCHEDULE.md` - Merged recurring sections

## Outstanding: Archive Pattern Design

Need to solve:
- Track "what we shipped this week" for client comms
- Keep project files noise-free (true SCD Type 1)
- Define grain: major accomplishments only (not trivial tasks)
- Make agent behavior explicit: when/how to archive

Design in progress - to be implemented after NËDL work session.

