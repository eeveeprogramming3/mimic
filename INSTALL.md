# Mimic Installation Guide

Step-by-step setup for first-time users.

## Step 1: Get the Code

```bash
git clone https://github.com/eeveeprogramming3/mimic.git
cd mimic
```

## Step 2: Create Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt.

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `mss` - for screenshots
- `pynput` - for input logging
- `Pillow` - for image processing
- `anthropic` - for Claude API

## Step 4: Get Claude API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **Settings > API Keys**
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-`)

## Step 5: Set API Key

**For current session:**
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx-your-key-here"
```

**Permanent (add to shell profile):**
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-xxxxx"' >> ~/.bashrc
source ~/.bashrc
```

## Step 6: Verify Installation

```bash
python main.py --help
```

You should see:
```
usage: mimic [-h] {start,stop,status,compile} ...

Record screen actions and generate automation skills for Moltbot
```

## Step 7: Test Recording

```bash
python main.py start test-recording
```

Click around, type something, then press `Ctrl+C`.

Check output:
```bash
ls recordings/test-recording/
```

You should see `screenshots/` and `actions.json`.

## Step 8: Test Compilation

```bash
python main.py compile test-recording
```

Check generated skill:
```bash
cat recordings/test-recording/SKILL.md
```

## Moltbot Integration

Skills are auto-saved to `~/.moltbot/skills/`. To use:

```bash
moltbot use test-recording
```

If Moltbot uses a different path, set it:
```bash
export MOLTBOT_SKILLS_DIR="/path/to/your/skills"
```

## You're Ready!

Run your first real recording:
```bash
python main.py start my-first-skill -c
```

The `-c` flag auto-compiles when you stop.

---

**Need help?** Open an issue on GitHub.
