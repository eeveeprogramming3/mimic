# Privacy Policy

**Last updated:** January 27, 2025

Mimic is a local-first tool. Your privacy is respected by design.

---

## Summary

| Data Type | Stored Locally | Sent to Cloud | Shared with Third Parties |
|-----------|----------------|---------------|---------------------------|
| Screenshots | Yes | Yes (Claude API)* | No |
| Mouse clicks | Yes | Yes (Claude API)* | No |
| Keyboard input | Yes | Yes (Claude API)* | No |
| Generated skills | Yes | No | No |
| API key | No (env var) | Yes (auth only) | No |
| Usage analytics | No | No | No |

*Only during compilation, and only to Anthropic's Claude API.

---

## What Data is Collected

### During Recording

When you run `mimic start <name>`, Mimic captures:

1. **Screenshots**
   - Full screen images every 2 seconds
   - Stored as PNG files locally
   - Location: `recordings/<task>/screenshots/`

2. **Mouse Events**
   - Click coordinates (X, Y)
   - Button pressed (left, right, middle)
   - Timestamp (seconds since recording started)

3. **Keyboard Events**
   - Keys pressed (characters and special keys)
   - Timestamp

All data is stored **locally on your machine** in the `recordings/` folder.

### During Compilation

When you run `mimic compile <name>`:

1. Screenshots are **resized** (max 1280px width)
2. Screenshots are **compressed** (JPEG, 70% quality)
3. Screenshots + actions JSON are sent to **Anthropic's Claude API**
4. Claude generates a SKILL.md file
5. Response is saved locally

**What is sent:**
- Compressed images (not originals)
- Action logs (clicks, keys with timestamps)
- A prompt asking Claude to generate a skill

**What is NOT sent:**
- Your full-resolution screenshots
- Any other files from your computer
- Your computer name or IP (beyond normal HTTPS)
- Any analytics or telemetry

---

## Data Storage

### Local Storage

| File | Location | Contains |
|------|----------|----------|
| Screenshots | `recordings/<task>/screenshots/` | PNG images |
| Actions log | `recordings/<task>/actions.json` | Clicks/keys |
| Generated skill | `recordings/<task>/SKILL.md` | Automation instructions |
| Config | `~/.mimic_config.json` | Your preferences |
| State | `.mimic_state.json` | Temporary recording state |

### Cloud Storage

Mimic does **NOT** store any data in the cloud.

When you compile, data is sent to Anthropic's API, processed, and returned. Anthropic's data retention policies apply to API calls. See: https://www.anthropic.com/privacy

---

## Third-Party Services

### Anthropic (Claude API)

- **Purpose:** AI-powered skill generation
- **Data sent:** Compressed screenshots, action logs
- **Their privacy policy:** https://www.anthropic.com/privacy
- **Data retention:** Per Anthropic's API terms (typically not used for training)

### No Other Services

Mimic does not use:
- Analytics (Google Analytics, Mixpanel, etc.)
- Crash reporting (Sentry, etc.)
- Telemetry of any kind
- Advertising networks

---

## Your Rights

### Access Your Data

All your data is stored locally. You can view it anytime:
```bash
ls -la recordings/
cat recordings/<task>/actions.json
```

### Delete Your Data

Delete specific recording:
```bash
rm -rf recordings/<task>
```

Delete all recordings:
```bash
rm -rf recordings/
```

Delete Mimic config:
```bash
rm ~/.mimic_config.json
```

### Export Your Data

Your data is already in portable formats:
- Screenshots: PNG files
- Actions: JSON file
- Skills: Markdown files

Copy them anywhere you like.

---

## Children's Privacy

Mimic is not intended for use by children under 13. We do not knowingly collect data from children.

---

## Changes to This Policy

We may update this policy as Mimic evolves. Changes will be noted in the CHANGELOG.md and this document's "Last updated" date.

---

## Contact

Questions about privacy? Open an issue: https://github.com/yourusername/mimic/issues

---

## Summary

**Mimic is designed for privacy:**
- All recordings stay on your machine
- Only compilation sends data (to Claude API)
- No analytics, no telemetry, no tracking
- You control your data completely
