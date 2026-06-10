# Contributing to free-ai-router

Thanks for your interest in contributing!

## How to Contribute

### Reporting Bugs

Open an issue with:
- Clear title describing the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, provider)
- Error messages (with secrets redacted!)

### Suggesting Features

Open an issue with:
- Use case description
- Proposed solution
- Alternatives considered

### Pull Requests

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test thoroughly: `python smart_router.py --test`
5. Update README/docs if needed
6. Commit with clear message
7. Push and open PR

## Adding a New Provider

To add a new AI provider:

1. Add config block in `router_config.json` (or `router_config.example.json`)
2. Test with `python smart_router.py --status`
3. Update `README.md` and `docs/PROVIDERS.md`
4. Add the provider to the setup wizard in `smart_router.py` if desired

## Code Style

- Python 3.8+ compatible
- Follow PEP 8
- Use type hints where possible
- Keep it simple — no over-engineering
- Comment non-obvious logic

## Security

**NEVER commit API keys, tokens, or secrets!**
- All `*.key.txt` files are gitignored
- The example config has no real keys
- If you accidentally commit a secret, rotate it immediately and use `git filter-branch` to remove from history

## Community

- WeChat Group: See README for QR code
- GitHub Issues: For bugs and feature requests
- GitHub Discussions: For questions and ideas
