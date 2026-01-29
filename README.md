# Mimic

**Record once, automate forever.**

Mimic watches you perform a task on your computer, then generates an AI-executable skill file that can replay it automatically. Built as an add-on for [Moltbot](https://github.com/moltbot/moltbot).

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

## What is Mimic?

Mimic is a CLI tool that:
1. **Records** your screen actions (screenshots, mouse clicks, keyboard inputs)
2. **Analyzes** the recording using Claude AI
3. **Generates** a SKILL.md file that Moltbot can execute automatically

Think of it as "teaching by demonstration" - show Mimic how to do something once, and it creates a reusable automation skill.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Claude API key ([get one here](https://console.anthropic.com/settings/keys))
- Moltbot installed (optional, but recommended)

---

### Linux (Ubuntu, Debian, Mint, Fedora)

**Option 1: pip install (easiest)**
```bash
pip install mimic-moltbot
```

**Option 2: From source**
```bash
git clone https://github.com/yourusername/mimic.git
cd mimic
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Set API key:**
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"

# Make permanent:
echo 'export ANTHROPIC_API_KEY="sk-ant-xxxxx"' >> ~/.bashrc
source ~/.bashrc
```

**Verify:**
```bash
mimic test
```

---

### macOS

**Option 1: pip install**
```bash
pip3 install mimic-moltbot
```

**Option 2: From source**
```bash
git clone https://github.com/yourusername/mimic.git
cd mimic
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Set API key:**
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"

# Make permanent:
echo 'export ANTHROPIC_API_KEY="sk-ant-xxxxx"' >> ~/.zshrc
source ~/.zshrc
```

**Grant permissions:**
- System Preferences → Security & Privacy → Privacy
- Enable **Screen Recording** for Terminal
- Enable **Accessibility** for Terminal

**Verify:**
```bash
mimic test
```

---

### Windows

**Option 1: pip install**
```powershell
pip install mimic-moltbot
```

**Option 2: From source**
```powershell
git clone https://github.com/yourusername/mimic.git
cd mimic
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

**Set API key:**
```powershell
# Current session:
$env:ANTHROPIC_API_KEY="sk-ant-xxxxx"

# Permanent (run as admin):
setx ANTHROPIC_API_KEY "sk-ant-xxxxx"
```

**Verify:**
```powershell
mimic test
```

---

## Quick Start

```bash
# Record a task and auto-compile to skill
mimic start my-task -c

# Do your task on screen...
# Press Ctrl+C when done

# Skill is generated and saved to ~/.moltbot/skills/my-task/
```

That's it! One command to learn a new skill.

---

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `mimic start <name>` | Start recording a task |
| `mimic start <name> -c` | Record and auto-compile |
| `mimic start <name> -p` | Record with privacy blur |
| `mimic start <name> -y` | Skip consent prompt |
| `mimic stop` | Stop recording |
| `mimic status` | Check if recording |
| `mimic compile <name>` | Compile recording to SKILL.md |
| `mimic compile <name> --model opus` | Use specific AI model |
| `mimic compile <name> --cost-estimate` | Show cost without compiling |
| `mimic test` | Verify setup and integration |
| `mimic install-trigger` | Install Moltbot chat trigger |

### Examples

**Basic recording:**
```bash
mimic start expense-report -c
# Do the task, Ctrl+C to stop
```

**With privacy blur (protects sensitive data):**
```bash
mimic start banking-task -p -c
```

**Skip consent prompt (for scripting):**
```bash
mimic start automated-task -y -c
```

**Choose AI model:**
```bash
mimic compile my-task --model opus    # Best quality
mimic compile my-task --model haiku   # Fastest/cheapest
```

---

## Moltbot Integration

Mimic automatically saves skills to `~/.moltbot/skills/`. To use from Moltbot chat:

```bash
# Install chat trigger skill
mimic install-trigger

# Reload Moltbot skills
molt skills reload
```

Now you can use in Telegram/Discord:
- `/mimic_start expense_report` - Start recording
- `/mimic_stop` - Stop recording
- `/mimic_compile expense_report` - Generate skill

---

## Output Structure

```
recordings/
  my-task/
    screenshots/          # Captured screens
    actions.json          # Mouse/keyboard log
    SKILL.md              # Generated skill

~/.moltbot/skills/
  my-task/
    SKILL.md              # Auto-installed for Moltbot
```

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | Required (or uses Moltbot's) |
| `MOLTBOT_SKILLS_DIR` | Custom skills path | `~/.moltbot/skills` |
| `MIMIC_MODEL` | Default AI model | `sonnet` |

Mimic automatically uses Moltbot's API key if available.

---

## Safety Features

- **Consent prompt** - Warns before recording
- **Privacy blur** (`-p`) - Blurs screenshots to protect sensitive data
- **Keystroke redaction** - Auto-redacts passwords and secrets
- **Sensitive field detection** - Warns when clicking password fields

---

## Troubleshooting

### "ModuleNotFoundError"
Activate your virtual environment:
```bash
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### "Already recording task"
Clear stale state:
```bash
rm -f .mimic_state.json .mimic_stop
```

### "No API key found"
Set your key or let Mimic use Moltbot's:
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
```

### macOS: "Screen recording not permitted"
Grant Terminal access in System Preferences → Security & Privacy → Screen Recording

### Linux: "Input monitoring not working"
Add yourself to input group:
```bash
sudo usermod -aG input $USER
# Log out and back in
```

See [FAQ.md](FAQ.md) for more solutions.

---

## Tech Stack

- **mss** - Screenshot capture
- **pynput** - Mouse/keyboard logging
- **Pillow** - Image processing
- **anthropic** - Claude API client

---

## Documentation

- [INSTALL.md](INSTALL.md) - Detailed setup guide
- [FAQ.md](FAQ.md) - Common questions
- [SECURITY.md](SECURITY.md) - Security practices
- [PRIVACY.md](PRIVACY.md) - Data handling
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

## License

MIT License - see [LICENSE](LICENSE)

---

## Links

- [Report Bug](https://github.com/yourusername/mimic/issues)
- [Request Feature](https://github.com/yourusername/mimic/issues)
- [Moltbot](https://github.com/moltbot/moltbot)

---

**Built with Claude API** | **Made for Moltbot**
# mimic
# mimic
