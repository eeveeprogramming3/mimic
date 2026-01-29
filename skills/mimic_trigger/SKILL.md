# Mimic - Skill Teaching Tool

## Description
Control Mimic (the skill teaching tool) directly from chat. Record your screen actions and generate automation skills without leaving the conversation.

## Commands

### Start Recording
**Trigger:** `/mimic_start <task_name>` or "mimic start <task_name>"

**Example:**
- `/mimic_start expense_report`
- `mimic start fill_form`

### Stop Recording
**Trigger:** `/mimic_stop` or "mimic stop"

### Check Status
**Trigger:** `/mimic_status` or "mimic status"

### Compile Recording
**Trigger:** `/mimic_compile <task_name>` or "mimic compile <task_name>"

**Example:**
- `/mimic_compile expense_report`
- `mimic compile my_task --model opus`

## Tool Definition

```json
{
  "name": "mimic_control",
  "description": "Control Mimic skill teaching tool - start/stop recording, compile skills",
  "input_schema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["start", "stop", "status", "compile", "test"],
        "description": "The Mimic action to perform"
      },
      "task_name": {
        "type": "string",
        "description": "Name for the task/skill (required for start/compile)"
      },
      "options": {
        "type": "object",
        "properties": {
          "privacy": {
            "type": "boolean",
            "description": "Enable privacy blur on screenshots"
          },
          "auto_compile": {
            "type": "boolean",
            "description": "Auto-compile after recording stops"
          },
          "model": {
            "type": "string",
            "enum": ["sonnet", "opus", "haiku"],
            "description": "AI model for compilation"
          }
        }
      }
    },
    "required": ["action"]
  }
}
```

## Execution Instructions

When the user requests a Mimic action:

### For "start" action:
1. Verify task_name is provided
2. Run shell command: `mimic start "<task_name>" -y` (with flags based on options)
   - Add `-p` if privacy mode requested
   - Add `-c` if auto_compile requested
3. Respond: "🎬 Recording started for '<task_name>'. Perform your task, then say 'mimic stop' when done."

### For "stop" action:
1. Run shell command: `mimic stop`
2. Respond: "⏹️ Recording stopped. Use '/mimic_compile <name>' to generate the skill."

### For "status" action:
1. Run shell command: `mimic status`
2. Return the output to user

### For "compile" action:
1. Verify task_name is provided
2. Run shell command: `mimic compile "<task_name>"` (with model flag if specified)
3. Wait for completion (may take 30-60 seconds)
4. Respond: "✅ Skill generated! You can now use '/<task_name>' to run it."

### For "test" action:
1. Run shell command: `mimic test`
2. Return the output showing integration status

## Example Conversation

**User:** mimic start expense_report
**Assistant:** 🎬 Recording started for 'expense_report'.
- I'm now capturing your screen and inputs
- Perform your expense report task normally
- Say "mimic stop" when you're done

**User:** mimic stop
**Assistant:** ⏹️ Recording stopped!
- Screenshots captured: 15
- Actions logged: 42
- Ready to compile. Say "mimic compile expense_report" to generate the skill.

**User:** mimic compile expense_report
**Assistant:** 🔄 Compiling 'expense_report' to SKILL.md...
📡 Sending to Claude API (Sonnet)...
✅ Skill generated!

Your new skill is ready:
- Location: ~/.moltbot/skills/expense_report/SKILL.md
- Run with: /expense_report

## Prerequisites
- Mimic must be installed: `pip install mimic-moltbot`
- ANTHROPIC_API_KEY must be set (or inherited from Moltbot config)
- Screen capture permissions (on macOS, grant in System Preferences)

## Notes
- Recording auto-stops after 60 seconds if not manually stopped
- Use privacy mode (-p) when recording sensitive workflows
- Skills are automatically installed to ~/.moltbot/skills/
- Run `mimic test` to verify setup before first use
