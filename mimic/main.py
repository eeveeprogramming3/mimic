#!/usr/bin/env python3
"""
Mimic - Record screen actions and generate automation skills
"""

import argparse
import base64
import io
import json
import os
import platform
import sys
import time
import threading
from pathlib import Path

import anthropic
import mss
from PIL import Image, ImageFilter, ImageDraw
from pynput import mouse, keyboard

# Try to import accessibility libraries (platform-specific)
ATSPI_AVAILABLE = False
try:
    import gi
    gi.require_version('Atspi', '2.0')
    from gi.repository import Atspi
    ATSPI_AVAILABLE = True
except (ImportError, ValueError):
    pass  # Not available on this system

# Directory where all recordings are saved
RECORDINGS_DIR = Path("./recordings")
# File that tracks the current recording session
STATE_FILE = Path("./.mimic_state.json")
# File that signals the recorder to stop
STOP_FILE = Path("./.mimic_stop")
# Config file for Mimic settings
CONFIG_FILE = Path.home() / ".mimic_config.json"
# Moltbot config file (to read API key)
MOLTBOT_CONFIG_FILE = Path.home() / ".moltbot" / "config.json"

# Common patterns that might indicate sensitive areas (coordinates to blur)
SENSITIVE_KEYWORDS = ["password", "secret", "token", "key", "credit", "ssn", "bank"]

# Supported models and their configurations
SUPPORTED_MODELS = {
    "sonnet": {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-5-20250929",
        "description": "Claude Sonnet 4.5 - Fast and capable (default)"
    },
    "opus": {
        "provider": "anthropic",
        "model_id": "claude-opus-4-5-20250114",
        "description": "Claude Opus 4.5 - Most capable, higher cost"
    },
    "haiku": {
        "provider": "anthropic",
        "model_id": "claude-haiku-3-5-20241022",
        "description": "Claude Haiku 3.5 - Fastest, lowest cost"
    }
}

DEFAULT_MODEL = "sonnet"


def load_moltbot_config():
    """Load Moltbot's config file to get API key and settings."""
    if not MOLTBOT_CONFIG_FILE.exists():
        return None

    try:
        config = json.loads(MOLTBOT_CONFIG_FILE.read_text())
        return config
    except (json.JSONDecodeError, IOError):
        return None


def get_api_key():
    """
    Get Anthropic API key with fallback chain:
    1. ANTHROPIC_API_KEY env var
    2. Moltbot's config.json
    3. Mimic's config.json
    """
    # 1. Check environment variable first
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return api_key

    # 2. Try Moltbot's config
    moltbot_config = load_moltbot_config()
    if moltbot_config:
        # Moltbot might store it as 'anthropic_api_key' or 'api_key' or nested
        api_key = moltbot_config.get("anthropic_api_key")
        if not api_key:
            api_key = moltbot_config.get("api_key")
        if not api_key:
            # Check nested structure
            providers = moltbot_config.get("providers", {})
            anthropic_config = providers.get("anthropic", {})
            api_key = anthropic_config.get("api_key")
        if api_key:
            return api_key

    # 3. Try Mimic's own config
    mimic_config = load_config()
    api_key = mimic_config.get("anthropic_api_key")
    if api_key:
        return api_key

    return None


def setup_api_key():
    """Ensure API key is available, setting env var if found in configs."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True  # Already set

    api_key = get_api_key()
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key
        return True

    return False


def get_model_config(model_name=None):
    """Get model configuration by name or from environment/config."""
    # Priority: argument > env var > config file > default
    if not model_name:
        model_name = os.environ.get("MIMIC_MODEL")

    if not model_name:
        config = load_config()
        model_name = config.get("model", DEFAULT_MODEL)

    if not model_name:
        model_name = DEFAULT_MODEL

    model_name = model_name.lower()

    if model_name not in SUPPORTED_MODELS:
        print(f"⚠️  Unknown model '{model_name}', using {DEFAULT_MODEL}")
        model_name = DEFAULT_MODEL

    return SUPPORTED_MODELS[model_name]


def apply_privacy_blur(img, blur_strength=35):
    """
    Apply heavy privacy blur to make ALL text unreadable.

    Strategy:
    1. Apply strong blur to completely obscure text
    2. Keep only basic shapes/colors for Claude to understand UI layout
    """
    # Apply heavy gaussian blur - text will be completely unreadable
    blurred = img.filter(ImageFilter.GaussianBlur(radius=blur_strength))

    # Apply a second pass for extra strength
    blurred = blurred.filter(ImageFilter.GaussianBlur(radius=20))

    # Blend: 90% blurred, 10% original (just enough to see color boundaries)
    blended = Image.blend(img, blurred, alpha=0.9)

    return blended


def apply_region_blur(img, regions):
    """
    Blur specific regions of an image.

    Args:
        img: PIL Image
        regions: List of (x, y, width, height) tuples to blur

    Returns:
        Image with specified regions blurred
    """
    result = img.copy()

    for x, y, w, h in regions:
        # Extract region
        box = (x, y, x + w, y + h)
        region = result.crop(box)

        # Blur it heavily
        blurred_region = region.filter(ImageFilter.GaussianBlur(radius=20))

        # Paste back
        result.paste(blurred_region, box)

    return result


def get_element_at_point(x, y):
    """
    Get accessibility information about the UI element at the given coordinates.
    Returns dict with role, name, description, or None if not available.
    """
    if not ATSPI_AVAILABLE:
        return None

    try:
        # Get the desktop (root of accessibility tree)
        desktop = Atspi.get_desktop(0)
        if not desktop:
            return None

        # Find the element at the given point
        element = Atspi.get_desktop(0)

        # Traverse to find the deepest element at point
        def find_at_point(obj, x, y):
            if obj is None:
                return None

            try:
                # Try to get component interface
                component = obj.get_component_iface()
                if component:
                    # Check if point is within this element
                    child = component.get_accessible_at_point(x, y, Atspi.CoordType.SCREEN)
                    if child and child != obj:
                        # Recurse into child
                        result = find_at_point(child, x, y)
                        if result:
                            return result
                        return child
            except:
                pass

            return obj

        # Try to find element at point using desktop's children (applications)
        for i in range(desktop.get_child_count()):
            try:
                app = desktop.get_child_at_index(i)
                if app:
                    component = app.get_component_iface()
                    if component:
                        child = component.get_accessible_at_point(x, y, Atspi.CoordType.SCREEN)
                        if child:
                            # Found an element, get its info
                            element = find_at_point(child, x, y) or child

                            # Extract useful information
                            role = element.get_role_name() if element else "unknown"
                            name = element.get_name() if element else ""
                            description = ""

                            try:
                                description = element.get_description() if element else ""
                            except:
                                pass

                            # Get parent info for context
                            parent_name = ""
                            try:
                                parent = element.get_parent()
                                if parent:
                                    parent_name = parent.get_name() or ""
                            except:
                                pass

                            return {
                                "role": role,
                                "name": name,
                                "description": description,
                                "parent": parent_name
                            }
            except:
                continue

        return None

    except Exception as e:
        # Silently fail - accessibility is optional
        return None


def get_default_moltbot_path():
    """Get the default Moltbot skills path based on OS."""
    system = platform.system()

    if system == "Windows":
        # Windows: %APPDATA%\moltbot\skills or %USERPROFILE%\.moltbot\skills
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "moltbot" / "skills"
        return Path.home() / ".moltbot" / "skills"

    elif system == "Darwin":
        # macOS: ~/Library/Application Support/moltbot/skills or ~/.moltbot/skills
        lib_path = Path.home() / "Library" / "Application Support" / "moltbot" / "skills"
        if lib_path.parent.parent.exists():
            return lib_path
        return Path.home() / ".moltbot" / "skills"

    else:
        # Linux and others: ~/.moltbot/skills
        return Path.home() / ".moltbot" / "skills"


def load_config():
    """Load Mimic config from file."""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config):
    """Save Mimic config to file."""
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_moltbot_skills_dir():
    """
    Get the Moltbot skills directory.
    Checks: env var > config file > default path > prompt user
    """
    # 1. Check environment variable
    env_path = os.environ.get("MOLTBOT_SKILLS_DIR")
    if env_path:
        path = Path(env_path).expanduser()
        if path.exists() or path.parent.exists():
            return path

    # 2. Check config file
    config = load_config()
    if "moltbot_skills_dir" in config:
        path = Path(config["moltbot_skills_dir"]).expanduser()
        if path.exists() or path.parent.exists():
            return path

    # 3. Try default path
    default_path = get_default_moltbot_path()
    if default_path.exists():
        return default_path

    # 4. Check if parent exists (Moltbot installed but no skills yet)
    if default_path.parent.exists():
        return default_path

    # 5. Prompt user
    print("⚠️  Moltbot skills folder not found at default location:")
    print(f"   {default_path}")
    print()
    print("Options:")
    print("  1. Enter custom path")
    print("  2. Use default anyway (will create folder)")
    print("  3. Skip Moltbot integration (save locally only)")
    print()

    choice = input("Choose [1/2/3]: ").strip()

    if choice == "1":
        custom_path = input("Enter Moltbot skills path: ").strip()
        if custom_path:
            path = Path(custom_path).expanduser()
            # Save to config for future
            config["moltbot_skills_dir"] = str(path)
            save_config(config)
            print(f"✅ Saved to config: {CONFIG_FILE}")
            return path

    elif choice == "2":
        return default_path

    elif choice == "3":
        return None

    # Default: use default path
    return default_path


def validate_moltbot_dir(path):
    """Validate we can write to the Moltbot skills directory."""
    if path is None:
        return False, "Moltbot integration skipped"

    try:
        # Try to create the directory
        path.mkdir(parents=True, exist_ok=True)

        # Test write permission
        test_file = path / ".mimic_test"
        test_file.write_text("test")
        test_file.unlink()

        return True, None

    except PermissionError:
        return False, f"Permission denied: {path}"
    except Exception as e:
        return False, f"Error: {e}"


def save_state(task_name, start_time):
    """Save current recording state to a file."""
    state = {
        "task_name": task_name,
        "start_time": start_time,
        "recording": True
    }
    STATE_FILE.write_text(json.dumps(state))


def load_state():
    """Load recording state from file. Returns None if not recording."""
    if not STATE_FILE.exists():
        return None
    return json.loads(STATE_FILE.read_text())


def clear_state():
    """Clean up state files."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    if STOP_FILE.exists():
        STOP_FILE.unlink()


def cmd_start(args):
    """Handle the 'start' command - begin recording a task."""
    task_name = args.name
    skip_consent = getattr(args, 'yes', False)

    # Check if already recording
    state = load_state()
    if state and state.get("recording"):
        print(f"❌ Already recording task: '{state['task_name']}'")
        print(f"   Run 'mimic stop' first")
        sys.exit(1)

    # Consent prompt (unless --yes flag)
    if not skip_consent:
        print("=" * 50)
        print("⚠️  RECORDING CONSENT")
        print("=" * 50)
        print()
        print("Mimic will capture:")
        print("  • Screenshots of your ENTIRE screen (every 2 sec)")
        print("  • All mouse clicks (coordinates)")
        print("  • All keyboard input (keys pressed)")
        print()
        print("⚠️  This may capture sensitive information like:")
        print("  • Passwords visible on screen")
        print("  • Personal data, financial info")
        print("  • Private messages")
        print()
        print("Recommendations:")
        print("  • Close sensitive apps/tabs before recording")
        print("  • Use --privacy (-p) flag to blur screenshots")
        print("  • Review recordings before compiling")
        print()

        # Ask for consent
        consent = input("Proceed with recording? [y/N]: ").strip().lower()
        if consent not in ('y', 'yes'):
            print("❌ Recording cancelled.")
            sys.exit(0)

        # Ask about privacy mode if not already set
        privacy_mode = getattr(args, 'privacy', False)
        if not privacy_mode:
            blur_choice = input("Enable privacy blur? [y/N]: ").strip().lower()
            if blur_choice in ('y', 'yes'):
                args.privacy = True
                print("🔒 Privacy mode enabled")

        print()

    # Create output directories
    task_dir = RECORDINGS_DIR / task_name
    screenshots_dir = task_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    # Clear any old stop signal
    if STOP_FILE.exists():
        STOP_FILE.unlink()

    # Save recording state
    start_time = time.time()
    save_state(task_name, start_time)

    privacy_mode = getattr(args, 'privacy', False)
    print(f"🎬 Recording started: '{task_name}'")
    print(f"   Saving to: {task_dir}/")
    if privacy_mode:
        print(f"   🔒 Privacy mode: ON (screenshots will be blurred)")
    print(f"   Press Ctrl+C to stop recording")
    print(f"   (or wait 60 seconds for auto-stop)")
    print()

    # List to store all recorded actions
    actions = []

    # Track if we've warned about sensitive areas
    sensitive_warning_shown = [False]  # Use list to allow mutation in nested func

    # Mouse click handler
    def on_click(x, y, button, pressed):
        if pressed:  # Only log when button is pressed, not released
            action = {
                "type": "click",
                "x": x,
                "y": y,
                "button": str(button),
                "timestamp": time.time() - start_time
            }

            # Try to get accessibility info for the clicked element
            element_info = get_element_at_point(x, y)
            is_sensitive = False

            if element_info:
                action["element"] = element_info
                elem_name = (element_info.get("name") or "").lower()
                elem_role = (element_info.get("role") or "").lower()
                elem_desc = element_info.get("name") or element_info.get("role", "unknown")

                # Check if element appears to be sensitive
                for keyword in SENSITIVE_KEYWORDS:
                    if keyword in elem_name or keyword in elem_role:
                        is_sensitive = True
                        action["sensitive"] = True
                        break

                # Also check for password input fields
                if elem_role in ("password text", "password", "secret"):
                    is_sensitive = True
                    action["sensitive"] = True

                if is_sensitive:
                    print(f"   🖱️  Click at ({x}, {y}) - ⚠️  [{element_info['role']}] {elem_desc} [SENSITIVE]")
                    if not sensitive_warning_shown[0]:
                        print(f"   ⚠️  WARNING: Clicked on potentially sensitive field!")
                        print(f"   ⚠️  Consider stopping and using --privacy mode")
                        sensitive_warning_shown[0] = True
                else:
                    print(f"   🖱️  Click at ({x}, {y}) - [{element_info['role']}] {elem_desc}")
            else:
                print(f"   🖱️  Click at ({x}, {y})")

            actions.append(action)

    # Keystroke buffer for grouping
    keystroke_buffer = []
    buffer_start_time = [None]  # Use list for mutation in nested func

    def flush_keystroke_buffer():
        """Flush buffered keystrokes as a single typed_text action."""
        if not keystroke_buffer:
            return

        typed_text = "".join(keystroke_buffer)
        timestamp = buffer_start_time[0] or (time.time() - start_time)

        # Check if text contains sensitive patterns
        is_sensitive = False
        text_lower = typed_text.lower()
        for keyword in SENSITIVE_KEYWORDS:
            if keyword in text_lower:
                is_sensitive = True
                break

        # Redact if sensitive
        if is_sensitive:
            display_text = "[REDACTED]"
            stored_text = "[REDACTED]"
        else:
            display_text = typed_text if len(typed_text) <= 20 else typed_text[:17] + "..."
            stored_text = typed_text

        action = {
            "type": "typed_text",
            "text": stored_text,
            "length": len(typed_text),
            "timestamp": timestamp
        }
        if is_sensitive:
            action["sensitive"] = True

        actions.append(action)
        print(f"   ⌨️  Typed: \"{display_text}\"" + (" [SENSITIVE]" if is_sensitive else ""))

        # Clear buffer
        keystroke_buffer.clear()
        buffer_start_time[0] = None

    # Keyboard handler
    def on_key_press(key):
        try:
            key_char = key.char  # Regular character key
            if key_char:
                # Start buffer timing on first char
                if buffer_start_time[0] is None:
                    buffer_start_time[0] = time.time() - start_time
                keystroke_buffer.append(key_char)
        except AttributeError:
            # Special key - flush buffer first, then log the special key
            flush_keystroke_buffer()

            key_name = str(key)
            action = {
                "type": "special_key",
                "key": key_name,
                "timestamp": time.time() - start_time
            }
            actions.append(action)

            # Only print certain special keys to reduce noise
            if key_name in ("Key.enter", "Key.tab", "Key.escape", "Key.backspace"):
                print(f"   ⌨️  {key_name.replace('Key.', '').upper()}")

    # Start input listeners in background threads
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_key_press)
    mouse_listener.start()
    keyboard_listener.start()

    # Screenshot capture loop
    screenshot_count = 0
    interval = 2  # seconds between screenshots
    max_duration = 60  # auto-stop after 60 seconds

    try:
        with mss.mss() as sct:
            while True:
                # Check for stop signal
                if STOP_FILE.exists():
                    print("\n⏹️  Stop signal received")
                    break

                # Check for timeout
                elapsed = time.time() - start_time
                if elapsed >= max_duration:
                    print(f"\n⏱️  Auto-stopping after {max_duration} seconds")
                    break

                # Capture screenshot
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = screenshots_dir / f"screen_{timestamp}_{screenshot_count:04d}.png"

                # Check if privacy mode is enabled
                privacy_mode = getattr(args, 'privacy', False)

                if privacy_mode:
                    # Capture to memory, apply blur, then save
                    screenshot = sct.grab(sct.monitors[0])
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    img = apply_privacy_blur(img)
                    img.save(str(filename))
                else:
                    sct.shot(output=str(filename))

                screenshot_count += 1

                privacy_indicator = " [BLURRED]" if privacy_mode else ""
                print(f"   📸 Screenshot {screenshot_count} saved ({int(elapsed)}s elapsed){privacy_indicator}")

                # Wait for next capture
                time.sleep(interval)

    except KeyboardInterrupt:
        print("\n⏹️  Stopped by Ctrl+C")

    # Flush any remaining keystrokes in buffer
    flush_keystroke_buffer()

    # Stop input listeners
    mouse_listener.stop()
    keyboard_listener.stop()

    # Save actions to JSON file
    actions_file = task_dir / "actions.json"
    actions_file.write_text(json.dumps(actions, indent=2))

    # Recording finished
    clear_state()
    print(f"\n✅ Recording complete!")
    print(f"   Screenshots saved: {screenshot_count}")
    print(f"   Actions logged: {len(actions)}")
    print(f"   Location: {task_dir}/")

    # Auto-compile if flag is set
    if args.compile:
        print()
        compile_recording(task_name)


def cmd_stop(args):
    """Handle the 'stop' command - end recording and compile skill."""
    state = load_state()

    if not state or not state.get("recording"):
        print("❌ No recording in progress")
        sys.exit(1)

    # Create stop signal file
    STOP_FILE.touch()
    print(f"⏹️  Stopping recording: '{state['task_name']}'")


def cmd_status(args):
    """Handle the 'status' command - check if recording is active."""
    state = load_state()

    if state and state.get("recording"):
        elapsed = int(time.time() - state["start_time"])
        print(f"📊 Recording in progress: '{state['task_name']}'")
        print(f"   Elapsed: {elapsed} seconds")
    else:
        print("📊 No recording in progress")


def estimate_cost(num_screenshots, num_actions):
    """
    Estimate API cost for compilation.

    Claude Sonnet pricing (as of Jan 2025):
    - Input: $3 per 1M tokens
    - Output: $15 per 1M tokens
    - Images: ~1,600 tokens per image (1280px)
    """
    # Estimate tokens
    image_tokens = num_screenshots * 1600  # ~1600 tokens per resized image
    text_tokens = 500 + (num_actions * 20)  # Base prompt + actions JSON
    input_tokens = image_tokens + text_tokens
    output_tokens = 2000  # Estimated SKILL.md output

    # Calculate cost
    input_cost = (input_tokens / 1_000_000) * 3.00
    output_cost = (output_tokens / 1_000_000) * 15.00
    total_cost = input_cost + output_cost

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost
    }


def compile_recording(task_name, cost_only=False, model_name=None):
    """Send recording to Claude and generate SKILL.md."""

    # Setup API key (from env, Moltbot config, or Mimic config)
    if not setup_api_key():
        print("❌ No API key found!")
        print("   Set via: export ANTHROPIC_API_KEY=sk-ant-...")
        print("   Or: Configure in Moltbot's ~/.moltbot/config.json")
        sys.exit(1)

    task_dir = RECORDINGS_DIR / task_name

    # Check recording exists
    if not task_dir.exists():
        print(f"❌ Recording not found: {task_dir}")
        sys.exit(1)

    screenshots_dir = task_dir / "screenshots"
    actions_file = task_dir / "actions.json"

    # Load actions
    if actions_file.exists():
        actions = json.loads(actions_file.read_text())
    else:
        actions = []

    # Load screenshots as base64
    screenshot_files = sorted(screenshots_dir.glob("*.png"))

    if not screenshot_files:
        print(f"❌ No screenshots found in {screenshots_dir}")
        sys.exit(1)

    # Limit to 25 screenshots max (evenly spaced)
    max_screenshots = 25
    total_screenshots = len(screenshot_files)
    if len(screenshot_files) > max_screenshots:
        step = len(screenshot_files) // max_screenshots
        screenshot_files = screenshot_files[::step][:max_screenshots]

    print(f"🔄 Compiling '{task_name}' to SKILL.md...")
    print(f"   Screenshots: {len(screenshot_files)} (of {total_screenshots} total)")
    print(f"   Actions: {len(actions)}")

    # Show cost estimate
    cost = estimate_cost(len(screenshot_files), len(actions))
    print()
    print(f"💰 Estimated API cost: ${cost['total_cost']:.4f}")
    print(f"   Input: ~{cost['input_tokens']:,} tokens (${cost['input_cost']:.4f})")
    print(f"   Output: ~{cost['output_tokens']:,} tokens (${cost['output_cost']:.4f})")

    if cost_only:
        print()
        print("ℹ️  Use 'mimic compile <name>' without --cost-estimate to proceed.")
        return

    print()

    # Build message content with images and actions
    content = []

    # Add each screenshot (resized + JPEG compressed)
    for i, img_path in enumerate(screenshot_files):
        # Open and resize image to max 1280px width
        img = Image.open(img_path)
        max_width = 1280
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # Convert to JPEG (much smaller than PNG)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        img_data = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

        content.append({
            "type": "text",
            "text": f"Screenshot {i+1} of {len(screenshot_files)}:"
        })
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": img_data
            }
        })

    # Check if any actions have element info
    has_element_info = any(a.get("element") for a in actions if a.get("type") == "click")

    # Add actions JSON
    element_note = ""
    if has_element_info:
        element_note = """
Note: Click actions include "element" data with accessibility information:
- "role": The type of UI element (button, text field, menu item, etc.)
- "name": The element's label or text
- "parent": The parent container's name

Use this semantic information to make the skill RESILIENT - reference elements by their
role and name (e.g., "click the Submit button") rather than coordinates. This ensures
the skill works even if the UI layout changes slightly.
"""

    content.append({
        "type": "text",
        "text": f"""
Here are the user's mouse clicks and keyboard inputs with timestamps:

```json
{json.dumps(actions, indent=2)}
```
{element_note}
Based on the screenshots and actions above, analyze what task the user performed.
Generate a SKILL.md file that automates this task using computer use tools.

The SKILL.md should:
1. Have a clear title and description of the task
2. List prerequisites (apps that need to be open, etc.)
3. Provide step-by-step instructions that an AI with computer-use tools can follow
4. Reference UI elements by their semantic names (from element data) when available, not just coordinates
5. Be robust and generalize to similar inputs
6. Use markdown formatting

IMPORTANT - Add a "Clarification Protocol" section that instructs the executing AI to:
- Before each major step, verify the expected UI state matches what's on screen
- If the UI looks significantly different (new layout, missing elements, unexpected dialog):
  1. PAUSE execution
  2. Take a screenshot of the current state
  3. Ask the user: "The interface looks different than expected. [describe what's different]. Should I: (a) attempt to adapt, (b) show you what I see, or (c) abort?"
- If an element cannot be found after 3 attempts, ask for user guidance
- This makes the skill ADAPTIVE - it learns from edge cases rather than failing silently

Return ONLY the SKILL.md content, nothing else.
"""
    })

    # Get model configuration
    model_config = get_model_config(model_name)
    model_id = model_config["model_id"]

    # Call Claude API
    print(f"📡 Sending to Claude API ({model_config['description'].split(' - ')[0]})...")
    client = anthropic.Anthropic()

    response = client.messages.create(
        model=model_id,
        max_tokens=4096,
        messages=[
            {"role": "user", "content": content}
        ]
    )

    skill_content = response.content[0].text

    # Save SKILL.md to recordings folder
    skill_file = task_dir / "SKILL.md"
    skill_file.write_text(skill_content)

    print(f"✅ Skill generated!")
    print(f"   Saved to: {skill_file}")

    # Also save to Moltbot skills folder (with detection)
    moltbot_base = get_moltbot_skills_dir()

    if moltbot_base:
        moltbot_task_dir = moltbot_base / task_name
        valid, error = validate_moltbot_dir(moltbot_task_dir)

        if valid:
            moltbot_skill_file = moltbot_task_dir / "SKILL.md"
            moltbot_skill_file.write_text(skill_content)
            print(f"   Installed to: {moltbot_skill_file}")
            print()
            print(f"🚀 Skill ready! Run with: moltbot use {task_name}")
        else:
            print(f"   ⚠️  Could not install to Moltbot: {error}")
            print(f"   Skill saved locally only.")
    else:
        print(f"   ℹ️  Moltbot integration skipped.")
        print(f"   To install manually, copy SKILL.md to your Moltbot skills folder.")
    print()
    print("--- SKILL.md Preview ---")
    print(skill_content[:500] + "..." if len(skill_content) > 500 else skill_content)


def cmd_compile(args):
    """Handle the 'compile' command - send recording to Claude and generate SKILL.md."""
    cost_only = getattr(args, 'cost_estimate', False)
    model_name = getattr(args, 'model', None)
    compile_recording(args.name, cost_only=cost_only, model_name=model_name)


def cmd_install_trigger(args):
    """Install the Mimic chat trigger skill to Moltbot."""
    import shutil

    # Find the bundled skill
    # When installed via pip, skills are in the package directory
    package_dir = Path(__file__).parent.parent
    skill_source = package_dir / "skills" / "mimic_trigger"

    # Fallback to current directory (for development)
    if not skill_source.exists():
        skill_source = Path("./skills/mimic_trigger")

    if not skill_source.exists():
        print("❌ Mimic trigger skill not found in package")
        print("   Try reinstalling: pip install --force-reinstall mimic-moltbot")
        sys.exit(1)

    # Get Moltbot skills directory
    moltbot_dir = get_moltbot_skills_dir()
    if not moltbot_dir:
        print("❌ Could not find Moltbot skills directory")
        sys.exit(1)

    # Install the skill
    skill_dest = moltbot_dir / "mimic_trigger"

    try:
        if skill_dest.exists():
            shutil.rmtree(skill_dest)
        shutil.copytree(skill_source, skill_dest)

        print("✅ Mimic chat trigger skill installed!")
        print(f"   Location: {skill_dest}")
        print()
        print("📱 You can now use these commands in Moltbot chat:")
        print("   /mimic_start <task_name>  - Start recording")
        print("   /mimic_stop               - Stop recording")
        print("   /mimic_compile <name>     - Generate skill")
        print("   /mimic_status             - Check recording status")
        print()
        print("💡 Tip: Run 'molt skills reload' to load the new skill immediately")

    except PermissionError:
        print(f"❌ Permission denied: {skill_dest}")
        print("   Try running with appropriate permissions")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error installing skill: {e}")
        sys.exit(1)


def cmd_test(args):
    """Handle the 'test' command - verify Mimic setup and Moltbot integration."""
    print("🔍 Mimic Integration Test")
    print("=" * 40)
    print()

    # Check OS
    system = platform.system()
    print(f"✅ Operating System: {system}")

    # Check Python
    print(f"✅ Python: {sys.version.split()[0]}")

    # Check dependencies
    print()
    print("Dependencies:")
    deps = ["mss", "pynput", "PIL", "anthropic"]
    for dep in deps:
        try:
            __import__(dep if dep != "PIL" else "PIL")
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - not installed")

    # Check API key (with source detection)
    print()
    env_key = os.environ.get("ANTHROPIC_API_KEY")
    if env_key:
        masked = env_key[:10] + "..." + env_key[-4:] if len(env_key) > 14 else "***"
        print(f"✅ API Key: {masked} (from environment)")
    else:
        # Try Moltbot config
        moltbot_config = load_moltbot_config()
        moltbot_key = None
        if moltbot_config:
            moltbot_key = moltbot_config.get("anthropic_api_key") or moltbot_config.get("api_key")
            if not moltbot_key:
                providers = moltbot_config.get("providers", {})
                anthropic_cfg = providers.get("anthropic", {})
                moltbot_key = anthropic_cfg.get("api_key")

        if moltbot_key:
            masked = moltbot_key[:10] + "..." + moltbot_key[-4:] if len(moltbot_key) > 14 else "***"
            print(f"✅ API Key: {masked} (from Moltbot config)")
        else:
            print("❌ API Key: Not found")
            print("   Set via: export ANTHROPIC_API_KEY=...")
            print("   Or: Moltbot will share its key automatically")

    api_key = get_api_key()  # For final status check

    # Check Moltbot
    print()
    print("Moltbot Integration:")
    default_path = get_default_moltbot_path()
    print(f"   Default path: {default_path}")

    config = load_config()
    if "moltbot_skills_dir" in config:
        print(f"   Config path: {config['moltbot_skills_dir']}")

    env_path = os.environ.get("MOLTBOT_SKILLS_DIR")
    if env_path:
        print(f"   Env var path: {env_path}")

    # Check if folder exists
    moltbot_dir = get_moltbot_skills_dir()
    if moltbot_dir:
        valid, error = validate_moltbot_dir(moltbot_dir)
        if valid:
            print(f"   ✅ Skills folder: {moltbot_dir}")

            # Count existing skills
            if moltbot_dir.exists():
                skills = [d for d in moltbot_dir.iterdir() if d.is_dir()]
                print(f"   ✅ Existing skills: {len(skills)}")
        else:
            print(f"   ❌ Error: {error}")

    # Check accessibility support
    print()
    print("Accessibility (smarter skills):")
    if ATSPI_AVAILABLE:
        print("   ✅ AT-SPI available - element detection enabled")
        print("   ℹ️  Clicks will capture button names, roles, etc.")
    else:
        print("   ⚠️  AT-SPI not available - using coordinates only")
        print("   ℹ️  Install 'python3-pyatspi' for smarter skills")

    # Show model info
    print()
    print("AI Model:")
    model_config = get_model_config()
    print(f"   Current: {model_config['description']}")
    print(f"   Change with: mimic compile <name> --model opus")
    print()
    print("   Available models:")
    for name, cfg in SUPPORTED_MODELS.items():
        marker = "→" if name == DEFAULT_MODEL else " "
        print(f"   {marker} {name}: {cfg['description']}")

    print()
    print("=" * 40)
    print("🎉 Mimic is ready!" if api_key else "⚠️  Set API key to compile skills")


def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        prog='mimic',
        description='Record screen actions and generate automation skills for Moltbot'
    )

    # Create subcommand parsers
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )

    # 'start' command
    start_parser = subparsers.add_parser(
        'start',
        help='Start recording a new task'
    )
    start_parser.add_argument(
        'name',
        type=str,
        help='Name for this task/skill (e.g., "open-browser", "fill-form")'
    )
    start_parser.add_argument(
        '-c', '--compile',
        action='store_true',
        help='Auto-compile to SKILL.md after recording stops'
    )
    start_parser.add_argument(
        '-p', '--privacy',
        action='store_true',
        help='Blur screenshots to protect sensitive information'
    )
    start_parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Skip consent prompt (for scripted/automated use)'
    )
    start_parser.set_defaults(func=cmd_start)

    # 'stop' command
    stop_parser = subparsers.add_parser(
        'stop',
        help='Stop recording and generate SKILL.md'
    )
    stop_parser.set_defaults(func=cmd_stop)

    # 'status' command
    status_parser = subparsers.add_parser(
        'status',
        help='Check recording status'
    )
    status_parser.set_defaults(func=cmd_status)

    # 'compile' command
    compile_parser = subparsers.add_parser(
        'compile',
        help='Send recording to Claude and generate SKILL.md'
    )
    compile_parser.add_argument(
        'name',
        type=str,
        help='Name of the recorded task to compile'
    )
    compile_parser.add_argument(
        '--cost-estimate',
        action='store_true',
        help='Show estimated API cost without compiling'
    )
    compile_parser.add_argument(
        '-m', '--model',
        type=str,
        choices=['sonnet', 'opus', 'haiku'],
        help='AI model to use: sonnet (default), opus (best), haiku (fast/cheap)'
    )
    compile_parser.set_defaults(func=cmd_compile)

    # 'test' command
    test_parser = subparsers.add_parser(
        'test',
        help='Verify Mimic setup and Moltbot integration'
    )
    test_parser.set_defaults(func=cmd_test)

    # 'install-trigger' command
    install_parser = subparsers.add_parser(
        'install-trigger',
        help='Install chat trigger skill to Moltbot (enables /mimic_start from chat)'
    )
    install_parser.set_defaults(func=cmd_install_trigger)

    # Parse arguments
    args = parser.parse_args()

    # If no command given, print help
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Run the appropriate command function
    args.func(args)


if __name__ == '__main__':
    main()
