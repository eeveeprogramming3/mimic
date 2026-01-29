# Contributing to Mimic

Thanks for wanting to contribute!

## How to Contribute

### Reporting Bugs
1. Check existing issues first
2. Open a new issue with:
   - What you expected
   - What actually happened
   - Steps to reproduce
   - Your OS and Python version

### Suggesting Features
1. Open an issue with `[Feature]` prefix
2. Describe the use case
3. Explain why it would be useful

### Submitting Code

1. **Fork the repo**
   ```bash
   git clone https://github.com/eeveeprogramming3/mimic.git
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Keep changes focused and small
   - Test your changes locally

4. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: description of what it does"
   ```

5. **Push and open PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a Pull Request on GitHub.

## Code Style

- Use Python 3.10+ features
- Follow PEP 8 guidelines
- Keep functions small and focused
- Add comments for complex logic
- No external dependencies without discussion

## Testing

Before submitting:
```bash
# Make sure it runs
python main.py --help

# Test recording
python main.py start test -c

# Check for syntax errors
python -m py_compile main.py
```

## Project Structure

```
mimic/
  main.py          # All core logic
  requirements.txt # Dependencies
  README.md        # Documentation
  examples/        # Sample outputs
```

## Questions?

Open an issue or reach out on X/Twitter.

Thanks for helping make Mimic better!
