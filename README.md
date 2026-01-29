# Mimic

Record once, automate forever.

Mimic watches you do a task on your computer, then generates a skill file that can replay it automatically. Built for [Moltbot](https://github.com/moltbot/moltbot).

## What it does

1. You run `mimic start my-task -c`
2. Do your task (click around, type stuff)
3. Hit Ctrl+C when done
4. Mimic sends the recording to Claude AI
5. Claude generates a SKILL.md that Moltbot can run

That's it. Teach once, run forever.

## Install

You need Python 3.10+ and a Claude API key.

**Linux/macOS:**
```
pip install mimic-moltbot
```

**Or from source:**
```
git clone https://github.com/eeveeprogramming3/mimic.git
cd mimic
pip install -e .
```

**Set your API key:**
```
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
```

If you have Moltbot installed, Mimic will use its API key automatically.

**Check it works:**
```
mimic test
```

## Usage

Record and compile in one go:
```
mimic start expense-report -c
```

With privacy blur (hides sensitive stuff):
```
mimic start banking-task -p -c
```

Just record (compile later):
```
mimic start my-task
mimic compile my-task
```

Pick your model:
```
mimic compile my-task --model opus
```

## Commands

| Command | What it does |
|---------|--------------|
| `mimic start <name>` | Start recording |
| `mimic start <name> -c` | Record + auto compile |
| `mimic start <name> -p` | Record with blur |
| `mimic stop` | Stop recording |
| `mimic compile <name>` | Generate skill from recording |
| `mimic test` | Check setup |
| `mimic install-trigger` | Add Moltbot chat commands |

## Moltbot integration

Skills get saved to `~/.moltbot/skills/` automatically.

To use from chat:
```
mimic install-trigger
molt skills reload
```

Then in Telegram: `/mimic_start expense_report`

## Safety stuff

- Asks for consent before recording
- `-p` flag blurs screenshots
- Auto-redacts typed passwords
- Warns if you click on password fields

## Files

After recording, you get:
```
recordings/my-task/
  screenshots/     <- what you saw
  actions.json     <- what you did
  SKILL.md         <- generated skill
```

## Troubleshooting

**"ModuleNotFoundError"** - activate your venv:
```
source .venv/bin/activate
```

**"Already recording"** - clear old state:
```
rm -f .mimic_state.json .mimic_stop
```

**"No API key"** - set it:
```
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
```

More help in [FAQ.md](FAQ.md)

## Docs

- [INSTALL.md](INSTALL.md) - detailed setup
- [FAQ.md](FAQ.md) - common issues
- [SECURITY.md](SECURITY.md) - security info
- [PRIVACY.md](PRIVACY.md) - data handling

## License

MIT
