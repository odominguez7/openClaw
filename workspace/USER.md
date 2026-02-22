# USER.md - About Your Human

*Learn about the person you're helping. Update this as you go.*

- **Name:** Omar
- **What to call them:** Omar
- **Pronouns:** *(optional)*
- **Timezone:** America/New_York (Boston) — ALWAYS use this for "today", "tomorrow", current time, and date calculations. Never assume UTC.
- **Notes:** MIT SFMBA ’26 student. Shared Spring class schedule.

## Context

- Timezone for “today/tomorrow” logic: **America/New_York (Boston)**.
- **Anti-mistake rule:** before sending any message that references "today", "tomorrow", weekday, or dates, always compute the current Boston datetime (America/New_York) and use that as the source of truth.
- Prefers agenda reminders as **just the list of events** (no extra commentary).
- For any **multi-day tasks list on request** (e.g., "tasks for next week"), format as: **group by class first, then by date**, and include DONE + 3-char key.
- **Formatting (WhatsApp):** in reminders/packs, always put **dates and hours in bold** using WhatsApp markdown: wrap them like `*Feb 12*` and `*1:00–2:30 pm*` for fastest scanning. (WhatsApp doesn’t support “black text” color; bold is the closest.)
- For Events lists: add a **blank line between each event** for quick scanning.

### Daily messaging rules (apply to every class going forward)

- **10:00 pm Boston (tomorrow preview):** send **3 separate messages**
  1) **Classes — <date>** (from class schedule)
  2) **Tasks — <date>** (readings are tasks; homework/prep/print/submit; include DONE phrase)
  3) **Events — <date>** (calendar meetings only; exclude homework/task blocks)
- **7:00 am Boston (today pack):** send **3 separate messages** (Classes / Tasks / Events for TODAY).
- **Follow-up rule for tasks:** start reminders **3 days before** due date (unless configured earlier for major deliverables) and keep following up **until Omar replies DONE <key3>**.
- **Follow-up cadence (default):** **9:00 am + 8:00 pm Boston** while pending inside the reminder window.
- Apply this follow-up behavior to **all tasks across all courses**.

### 3-pack formatting (Classes / Tasks / Events)
- For the daily 3-pack messages, format each message **grouped by class first**, then by **date/time**.
- For the **Events** message: group into **Other events** only (no "Class events" section). If a calendar event is clearly a class session that is already in "Today's classes", do not repeat it in Events.

### Always include titles

- For **every** class-related reminder/message, always include **course number + class title**.
- For assignment follow-ups, always include the **class title** and the **due date** (not just "any update").

### Formatting specifics

- For the daily classes reminder, start with exactly: "Good morning Omar, this are your classes of the day".
- For 15.281 reminders, always use the **full task name** (no IDs).
- When sending “rest of week” / multi-day class lists, **do not add meta-notes** like “If X isn’t happening tell me…”. If a schedule discrepancy needs confirmation (e.g., Fri 15.871 rec), ask as a separate, direct question (not appended to the 3-pack).

*(What do they care about? What projects are they working on? What annoys them? What makes them laugh? Build this over time.)*

---

The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference.

## Data Sources (CRITICAL — never mix these up)
- **Classes** = read from `/home/odominguez7/.openclaw/workspace/schedule.json` (weekly recurring schedule)
- **Events** = run `vdirsyncer sync && khal list <date>` (iCloud calendar — meetings, events, deadlines)
- **Tasks** = read from `/home/odominguez7/.openclaw/workspace/memory/tasks-*.json` files
- NEVER show classes as events. NEVER show events as classes. These are separate sources.
