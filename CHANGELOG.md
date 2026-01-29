# Changelog

All notable changes to Mimic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-27

### Added
- Initial release of Mimic
- **Recording features:**
  - Screenshot capture every 2 seconds (mss)
  - Mouse click logging with coordinates (pynput)
  - Keyboard input logging (pynput)
  - 60-second auto-timeout
  - Ctrl+C to stop recording
- **Compilation features:**
  - Claude API integration (Sonnet model)
  - SKILL.md generation from recordings
  - Image compression (JPEG, max 1280px width)
  - Limit to 25 screenshots maximum
  - `--cost-estimate` flag to preview API costs
- **CLI commands:**
  - `mimic start <name>` - Start recording
  - `mimic start <name> -c` - Record and auto-compile
  - `mimic stop` - Stop recording
  - `mimic status` - Check recording status
  - `mimic compile <name>` - Compile recording to SKILL.md
  - `mimic compile <name> --cost-estimate` - Preview cost
  - `mimic test` - Verify setup and integration
- **Moltbot integration:**
  - Auto-detect skills folder (Linux, macOS, Windows)
  - Prompt user if folder not found
  - Config file support (`~/.mimic_config.json`)
  - Environment variable support (`MOLTBOT_SKILLS_DIR`)
  - Write permission validation
- **Packaging:**
  - PyPI-ready structure (pyproject.toml)
  - `mimic` CLI command after pip install
- **Documentation:**
  - README.md with full setup guide
  - INSTALL.md quickstart
  - FAQ.md troubleshooting
  - CONTRIBUTING.md guidelines
  - Example skill files

### Security
- API keys via environment variables only (never hardcoded)
- Local-only recording (no cloud upload of screenshots)
- User-initiated recording only

---

## [Unreleased]

### Planned
- Chat trigger skill (`/mimic_start` from Moltbot)
- `--privacy-mode` flag (blur sensitive areas)
- Multi-model support (Gemini, local models)
- `--share` flag for marketplace upload
- Accessibility tree capture
- Unit tests
