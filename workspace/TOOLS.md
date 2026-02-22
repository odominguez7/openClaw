# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Twilio
- Credential (from Omar, 2026-02-20): 1GAJE96UPVGHP95D9L5GE2R9

### Links
- VMS Office hours (Calendly): https://calendly.com/mitvmsofficehours

### Google Sheets pixel art standard
- Default render: 120×120 cells, 96-color adaptive palette
- Resample: LANCZOS downsample
- Dither: Floyd-Steinberg
- Cell size: 5 px (rows + cols)
- Target tab format: paint backgroundColor for each cell starting at A1

### Calendar Management (CRITICAL — iCloud via vdirsyncer + khal)

**NEVER use `khal edit` or `khal delete` — they require interactive TTY and ALWAYS fail from WhatsApp.**

#### Delete an event:
```bash
FILE=$(grep -rl "EVENT NAME" ~/.local/share/vdirsyncer/calendars/ | head -1)
rm "$FILE" && vdirsyncer sync && echo "Deleted."
```

#### Reschedule an event (change date):
```bash
FILE=$(grep -rl "EVENT NAME" ~/.local/share/vdirsyncer/calendars/ | xargs grep -l "OLD_DATE" | head -1)
sed -i "s/OLD_DATE/NEW_DATE/g" "$FILE"
rm -f ~/.local/share/khal/khal.db && vdirsyncer sync && echo "Rescheduled."
```

#### View events:
```bash
khal list today 7d
khal search "event name"
```

Always end with `vdirsyncer sync` to push changes to iCloud.
