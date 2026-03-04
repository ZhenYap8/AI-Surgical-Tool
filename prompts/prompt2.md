Update the front-end so the “Surgeon Profile Module” is no longer a single static form. It should become a clickable “Profile” system where users can create, view, and edit multiple surgeon profiles.

Implement the following UI + behaviour:

1) Profile Entry Point
- Replace the current module with a compact “Profile Selector” header:
  - Title: “Surgeon Profiles”
  - A dropdown (or list) to select an existing profile by name
  - Button: “+ Add Profile”
  - Button: “Edit”
- When a profile is selected, show a read-only summary card (name, grade, years, procedure count, skill tags).

2) Profile Drawer / Modal
- Clicking “+ Add Profile” or “Edit” opens a modal (or right-side drawer) with a form.
- The form saves to local state and persists to localStorage (for now).
- Support CRUD:
  - Create new profile
  - Update existing profile
  - Delete profile (with confirm)

3) Inside the profile form, there are TWO tag sections:

A) Tag Section 1: Doctor Experience (Grade)
- Label: “Doctor Experience”
- Required single-select field: “Surgeon Grade”
- Use a pill/tag UI (not a dropdown) with options like:
  - CT1, CT2
  - ST1, ST2, ST3, ST4, ST5, ST6, ST7
  - Consultant (<5 years), Consultant (5+ years)
- Only ONE grade can be selected at a time.
- Store as: profile.grade

B) Tag Section 2: Skillsets (Hashtag-style)
- Label: “Skillsets”
- Input box where user types a skill and presses Enter to add a tag (like hashtags).
- Tags appear as removable chips/pills.
- Prevent duplicates (case-insensitive).
- Max 12 tags, and max 20 characters per tag.
- Example placeholder: “Type a skill and press Enter (e.g., cataract, laparoscopy, robotics)”
- Store as: profile.skills (string array)

4) Profile Fields
In the same modal, include:
- Profile name (required)
- Procedures performed (number input)
- Risk/Consistency index (0–10 slider) + live numeric value
- (Optional) Primary procedure type (text or select)

5) Data Model
Use this shape:
{
  id: string,
  name: string,
  grade: string,
  proceduresPerformed: number,
  riskIndex: number,
  skills: string[],
  createdAt: number,
  updatedAt: number
}

6) UX/Styling Requirements
- Keep the design clean and clinical.
- Tags should look like “chips” with an X to remove.
- Use consistent spacing and alignment with the rest of the module.
- The selected grade pill should visually highlight.
- Provide validation errors inline (e.g., missing name or grade).

Return the updated component code with:
- Profile selector UI
- Modal/drawer form
- localStorage persistence
- Tag section 1 (single-select grade chips)
- Tag section 2 (hashtag-style skill chips)