# Surgeon Profile Module — Implemented Spec

This document describes the **current implemented state** of the Surgeon Profile Module in the frontend (`web/src/App.jsx` + `web/src/App.css`).

---

## Overview

The Surgeon Profile Module replaces a static form with a multi-profile system. Users can create, view, edit, and delete named surgeon profiles. A selected profile automatically calibrates the prediction engine (e.g. auto-sets experience level from grade).

---

## 1. Profile Entry Point (Card in Left Panel)

A `profile-card` component sits at the top of the left input panel. It contains:

- **Card header row**: title `"Surgeon Profiles"` (left) + `"+ Add Profile"` button (right, blue pill style)
- **Profile selector row**: a `<select>` dropdown listing all saved profiles by name, with an inline `Edit` button that appears only when a profile is selected
- **Read-only Summary Card** (shown when a profile is selected):
  - Profile name (bold)
  - Grade pill (highlighted, same style as modal pill)
  - Primary procedure (if set)
  - Procedures performed count
  - Risk Index badge (`RI X / 10`)
  - Skill hashtag chips (`#skill`)
  - An `Edit` button (top-right of card)
- **Empty state** (shown when no profile is selected): ghost icon + hint text

---

## 2. Profile Modal

Clicking `"+ Add Profile"` or `"Edit"` opens a centred modal overlay (`modal-overlay` → `modal-content`) with a smooth slide-in animation.

Clicking outside the modal (on the overlay) closes it.

**Modal structure:**
- `modal-header`: title (`"New Surgeon Profile"` or `"Edit Profile"`) + `✕` close button
- `modal-body`: scrollable form content
- `modal-footer`: `Delete Profile` button (red, left, only on edit) + `Cancel` / `Save Changes` or `Create Profile` buttons (right)

---

## 3. Profile Form Fields

### Basic Fields (inside `modal-body`)

| Field | Type | Notes |
|-------|------|-------|
| Full Name | Text input | Required. Shows inline error if empty. |
| Total Procedures | Number input | Min 0. Stored as `proceduresPerformed`. |
| Primary Procedure | Text input | Optional. e.g. "Laparoscopic Cholecystectomy" |

### Tag Section 1 — Doctor Experience (Grade)

- **Label**: `"Doctor Experience *"`
- **Helper text**: "Select one grade — this auto-sets the experience level in the prediction engine."
- **UI**: A wrapping row of pill/chip buttons (`grade-pills` → `grade-pill`)
- **Behaviour**: Single-select only. Selected pill gets `.selected` class (solid blue fill, white text). Clicking another grade deselects the previous one.
- **Options**:
  - Core Trainee: `CT1`, `CT2`
  - Specialty Trainee: `ST1`, `ST2`, `ST3`, `ST4`, `ST5`, `ST6`, `ST7`
  - Consultant: `Consultant (<5 yrs)`, `Consultant (5+ yrs)`
- **Stored as**: `profile.grade` (string)
- **Validation**: Required. Shows inline error if not selected on save.

### Tag Section 2 — Skillsets (Hashtag-style)

- **Label**: `"Skillsets"` + tag count badge (`X / 12`, right-aligned)
- **Helper text**: "Type a skill and press Enter to add it as a tag."
- **UI**: `tag-input-container` — a flex-wrap box containing existing chips + a live inline text input
- **Chip style** (`edit-chip`): `#skillname` with a `✕` remove button
- **Behaviour**:
  - Press `Enter` to add the current input value as a chip
  - Normalised to lowercase, trimmed
  - Duplicates silently ignored (no error)
  - Max **12 tags**, max **20 characters** per tag
  - Input disabled when at 12 tags
  - Placeholder changes: empty → long hint; has tags → `"Add another…"`; full → `""`
- **Stored as**: `profile.skills` (string array)

### Risk / Consistency Index Slider

- **Label**: `"Risk / Consistency Index"` + live value badge (right-aligned)
- **Range**: 0–10
- **Labels**: `"0 — Fast / Risky"` (left) · `"10 — Slow / Cautious"` (right)
- **Stored as**: `profile.riskIndex` (number)

---

## 4. Grade → Experience Level Auto-Mapping

When a profile is selected from the dropdown, the `experience_level` field in the Training Parameters form is automatically updated using this map:

| Grade | Experience Level |
|-------|----------------|
| CT1, CT2, ST1, ST2 | novice |
| ST3, ST4, ST5 | intermediate |
| ST6, ST7, Consultant (<5 yrs), Consultant (5+ yrs) | advanced |

An `auto` green badge appears next to the Experience Level label when a profile is active.

---

## 5. Data Model

```js
{
  id: string,              // generated: Date.now().toString(36) + random
  name: string,            // required
  grade: string,           // required, e.g. "ST3"
  proceduresPerformed: number,
  primaryProcedure: string, // optional
  riskIndex: number,       // 0–10
  skills: string[],        // lowercase, max 12
  createdAt: number,       // Unix ms timestamp
  updatedAt: number        // Unix ms timestamp
}
```

---

## 6. Persistence

Profiles are saved to **`localStorage`** under the key `"surgeon_profiles"` as a JSON array. State is re-read on mount and written on every change via `useEffect`.

---

## 7. CRUD Behaviour

| Action | Trigger | Result |
|--------|---------|--------|
| Create | `"+ Add Profile"` → fill form → `"Create Profile"` | New profile added, auto-selected in dropdown |
| Read | Select from dropdown | Summary card rendered read-only |
| Update | `"Edit"` → change fields → `"Save Changes"` | Profile updated in-place, `updatedAt` refreshed |
| Delete | `"Edit"` → `"Delete Profile"` → `window.confirm` | Profile removed, dropdown reset to empty |

---

## 8. Validation

- **Name**: required — shows `"Name is required."` below the input if empty on save attempt
- **Grade**: required — shows `"Please select a grade."` below the pill group if none selected on save attempt
- Validation re-runs on every save attempt; errors clear on the next successful save

---

## 9. CSS Classes Reference

| Class | Purpose |
|-------|---------|
| `.profile-card` | Outer card wrapper |
| `.btn-add-profile` | Blue pill `"+ Add Profile"` button |
| `.profile-selector-row` | Flex row: dropdown + Edit button |
| `.profile-select` | The `<select>` element, `flex: 1` |
| `.btn-edit-inline` | Edit button beside the dropdown |
| `.profile-summary-card` | Read-only selected profile display |
| `.profile-name` | Bold name in summary card |
| `.profile-meta` | Flex row of grade pill + meta items |
| `.ri-badge` | Grey pill showing `RI X / 10` |
| `.btn-edit-profile` | Edit button inside summary card |
| `.skill-chip` | Read-only `#skill` chip in summary |
| `.profile-empty` | Empty state hint block |
| `.grade-pills` | Flex-wrap row of grade buttons |
| `.grade-pill` | Individual grade button |
| `.grade-pill.selected` | Active/selected grade (solid blue) |
| `.grade-pill.mini` | Smaller variant used in summary card |
| `.tag-input-container` | Chip + input flex-wrap box |
| `.edit-chip` | Removable skill chip in modal |
| `.chip-remove` | `✕` button inside chip |
| `.tag-input` | Inline text input inside chip box |
| `.tag-count` | `"X / 12"` counter badge |
| `.modal-overlay` | Full-screen dimmed backdrop |
| `.modal-content` | White modal card |
| `.modal-header` | Title + close button row |
| `.modal-body` | Scrollable form area |
| `.modal-footer` | Delete (left) + Cancel/Save (right) |
| `.auto-badge` | Green `"auto"` badge on Experience label |