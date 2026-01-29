# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in Mimic, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email: [your-email@example.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to resolve the issue.

---

## Security Considerations

### API Key Handling

- **Storage:** API keys are read from environment variables only (`ANTHROPIC_API_KEY`)
- **Never hardcoded:** Keys are not stored in code, config files, or git
- **User responsibility:** Keep your API key secret; rotate if compromised

**Best practices:**
```bash
# Set in current session only
export ANTHROPIC_API_KEY="sk-ant-xxxxx"

# Or in ~/.bashrc (more permanent, but ensure file permissions)
echo 'export ANTHROPIC_API_KEY="sk-ant-xxxxx"' >> ~/.bashrc
chmod 600 ~/.bashrc
```

### Screen Recording Privacy

**What gets captured:**
- Full screen screenshots (everything visible)
- All mouse clicks (coordinates, button, timestamp)
- All keyboard input (keys pressed, timestamp)

**Risks:**
- Passwords visible on screen
- Sensitive data (bank accounts, private messages)
- Personal information

**Mitigations:**
1. Close sensitive apps/tabs before recording
2. Review screenshots before compiling:
   ```bash
   ls recordings/<task>/screenshots/
   # Delete any sensitive ones manually
   ```
3. Recordings stay local until you compile
4. Only compiled SKILL.md is sent to API (not raw screenshots in final skill)

### Data Transmission

**What is sent to Claude API:**
- Compressed screenshots (JPEG, resized)
- Mouse/keyboard action logs (JSON)
- Compilation prompt

**What is NOT sent:**
- Your API key in logs
- System information
- Other files on your computer

**Network security:**
- All API calls use HTTPS
- Anthropic's API handles encryption

### Local Storage

**Files created:**
- `recordings/<task>/screenshots/*.png` - Local only
- `recordings/<task>/actions.json` - Local only
- `recordings/<task>/SKILL.md` - Local + Moltbot folder
- `~/.mimic_config.json` - Your preferences (no secrets)
- `.mimic_state.json` - Temporary recording state

**Cleanup:**
```bash
# Delete a recording
rm -rf recordings/<task>

# Delete all recordings
rm -rf recordings/

# Clear Mimic config
rm ~/.mimic_config.json
```

### Permissions Required

**Linux:**
- Read/write to current directory
- Read/write to `~/.moltbot/skills/`
- Screen capture (X11/Wayland)
- Input monitoring (may need `input` group)

**macOS:**
- Screen Recording permission (System Preferences)
- Accessibility permission (for input logging)

**Windows:**
- No special permissions typically needed

---

## Security Checklist for Users

Before recording:
- [ ] Close password managers
- [ ] Close banking/financial apps
- [ ] Close private messaging apps
- [ ] Close any sensitive documents
- [ ] Consider using a clean desktop/workspace

After recording:
- [ ] Review screenshots in `recordings/<task>/screenshots/`
- [ ] Delete any that captured sensitive data
- [ ] Check `actions.json` for any sensitive keystrokes

Before sharing skills:
- [ ] Review the generated SKILL.md
- [ ] Ensure no sensitive paths/data leaked into instructions
- [ ] Test the skill in a safe environment first

---

## Known Limitations

1. **No encryption at rest:** Recordings are stored as plain files
2. **No automatic redaction:** Sensitive data is not auto-detected
3. **No audit logging:** No log of who recorded what
4. **Single-user design:** Not intended for shared/enterprise environments

---

## Future Security Improvements

- [ ] `--privacy-mode` to blur detected sensitive areas
- [ ] Auto-detect and warn about visible passwords
- [ ] Encrypted local storage option
- [ ] Recording consent prompts
- [ ] Audit logging
