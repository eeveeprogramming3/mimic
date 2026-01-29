# Frequently Asked Questions (FAQ)

## Installation Issues

### "ModuleNotFoundError: No module named 'mss'" (or pynput, PIL, anthropic)

**Cause:** Virtual environment not activated or dependencies not installed.

**Fix:**
```bash
cd ~/mimic-project
source .venv/bin/activate
pip install -r requirements.txt
```

### "pip install mimic-moltbot" fails

**Cause:** Package not published to PyPI yet, or Python version too old.

**Fix:**
```bash
# Install from GitHub instead
pip install git+https://github.com/eeveeprogramming3/mimic.git

# Or install locally
git clone https://github.com/eeveeprogramming3/mimic.git
cd mimic
pip install -e .
```

---

## Recording Issues

### "Already recording task: 'xyz'"

**Cause:** Previous recording didn't finish cleanly.

**Fix:**
```bash
rm -f .mimic_state.json .mimic_stop
```

### Recording doesn't capture my clicks/keys

**Cause:** On Linux, pynput may need root or input group permissions.

**Fix:**
```bash
# Add yourself to input group
sudo usermod -aG input $USER
# Log out and back in, then try again
```

### Screenshots are black or empty

**Cause:** Wayland display server (common on newer Ubuntu/Fedora).

**Fix:** Switch to X11 session at login, or run:
```bash
export XDG_SESSION_TYPE=x11
```

---

## Compilation Issues

### "Request too large" error

**Cause:** Too many screenshots or images too large.

**Fix:** Already handled - Mimic limits to 25 screenshots and compresses to JPEG. If still failing:
```bash
# Delete some screenshots manually
ls recordings/my-task/screenshots/ | head -20 | xargs -I{} rm recordings/my-task/screenshots/{}
```

### "Could not resolve authentication method"

**Cause:** API key not set.

**Fix:**
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
```

To make it permanent:
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-xxxxx"' >> ~/.bashrc
source ~/.bashrc
```

### "Rate limit exceeded" or "429 Too Many Requests"

**Cause:** Too many API calls in short time.

**Fix:** Wait a few minutes and try again. Check your API usage at console.anthropic.com.

### Compilation takes forever / times out

**Cause:** Large payload or slow connection.

**Fix:**
- Check your internet connection
- Reduce screenshot count (shorter recordings)
- Check API status at status.anthropic.com

---

## Moltbot Integration Issues

### "Moltbot skills folder not found"

**Cause:** Moltbot not installed or installed in non-standard location.

**Fix:** When prompted, either:
1. Enter the correct path manually
2. Choose "Use default anyway" to create the folder
3. Set environment variable: `export MOLTBOT_SKILLS_DIR=/your/path`

### Skill doesn't appear in Moltbot

**Cause:** Moltbot needs to reload skills.

**Fix:**
```bash
molt skills reload
# Or restart Moltbot
molt restart
```

### "Permission denied" when saving skill

**Cause:** No write access to Moltbot skills folder.

**Fix:**
```bash
chmod 755 ~/.moltbot/skills
# Or run mimic with appropriate permissions
```

---

## Cost & API Questions

### How much does compilation cost?

**Typical cost:** $0.05 - $0.15 per skill (depending on screenshots/actions).

**Check before compiling:**
```bash
mimic compile my-task --cost-estimate
```

### Can I use a different AI model?

**Currently:** Mimic uses Claude Sonnet. Multi-model support is planned.

**Workaround:** Modify `mimic/main.py` line ~419 to change the model.

---

## General Questions

### Can I record sensitive data (passwords, bank info)?

**Warning:** Screenshots capture EVERYTHING on screen. Avoid recording sensitive data.

**Best practice:**
- Close sensitive apps/tabs before recording
- Review screenshots in `recordings/<task>/screenshots/` before compiling
- Delete any sensitive screenshots manually

### How long can I record?

**Default:** 60 seconds (auto-stops).

**Workaround:** Start multiple recordings and compile the best one.

### Can I edit the generated SKILL.md?

**Yes!** The generated file is plain Markdown. Edit it at:
- `recordings/<task>/SKILL.md` (local copy)
- `~/.moltbot/skills/<task>/SKILL.md` (Moltbot copy)

---

## Still stuck?

Open an issue: https://github.com/eeveeprogramming3/mimic/issues
