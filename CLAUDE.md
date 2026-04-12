# Development Guide

## Setup

Install all dependencies (runtime + dev):

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

## After making any code changes

Always run lint and tests before committing:

```bash
flake8 main.py tests/
pytest
```

Both must pass with zero errors/failures.

## Adding new functionality

- Add corresponding tests in `tests/test_client.py`
- New `Client` methods: test via `patch.object(client, '_remote_control')` or by mocking `client.session.post`
- New top-level functions: mock their external dependencies (`requests.post`, `zeroconf`, etc.)

## Lint rules

Configured in `.flake8` — max line length is 120. Do not use bare `f"..."` strings without `{}` placeholders.
