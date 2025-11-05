# Project Improvement Suggestions

## Critical Issues

### 1. Security Vulnerabilities

#### API Key Exposure
- **Issue**: API key is written to shell config files in plaintext (`install.sh:23,30,37`)
- **Impact**: Keys could be committed to version control or exposed in backups
- **Fix**:
  - Use a config file in `~/.config/perplexity/` instead
  - Add proper permissions (chmod 600)
  - Consider using system keyring (keyring package)

#### Input Validation
- **Issue**: No validation on user input before sending to API
- **Impact**: Potential injection attacks or unexpected API behavior
- **Fix**: Add input sanitization and length limits

### 2. Bug Fixes

#### Color Function Bug in hi_settings.py:10
```python
# Current (broken):
return f"[{color}]{text}\033"

# Should be:
return f"[{color}]{text}[/]"
```

#### Typo in Environment Variable
- README and code use `PERPLIXITY_API_KEY` (typo) in places
- Should consistently be `PERPLEXITY_API_KEY`

#### Missing Error Handling
- `hi:161` - `sys.stdin.read()` can block indefinitely
- `hi_settings.py:86` - subprocess calls lack timeout
- No handling for network failures or rate limiting

---

## High Priority Improvements

### 3. Code Quality & Maintainability

#### Add Type Hints
```python
# Example improvements:
def preparePayload(
    model: str = CONST.AVAILABLE_MODELS[0],
    context: str = CONST.DEFAULT_CONTEXT,
    args: argparse.Namespace = argparse.Namespace()
) -> dict[str, Any]:
    ...

def color(text: str, color: str) -> str:
    ...
```

#### Reduce Code Duplication
- `color()` function exists in both `hi` and `hi_settings.py`
- Similar error handling patterns repeated throughout

#### Use Logging Instead of Print
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Starting chat session")
logger.error(f"API request failed: {e}")
```

#### Add Configuration File Support
```python
# ~/.config/perplexity/config.toml
[api]
key = "pplx-..."
timeout = 7200

[defaults]
model = "sonar"
context = "..."

[display]
colors_enabled = true
```

### 4. Architecture Improvements

#### Separate Concerns
Create proper module structure:
```
perplexity_cli/
├── __init__.py
├── __main__.py      # Entry point
├── api/
│   ├── __init__.py
│   ├── client.py    # API client
│   └── models.py    # Pydantic models
├── cli/
│   ├── __init__.py
│   ├── parser.py    # Argument parsing
│   └── interface.py # User interaction
├── config/
│   ├── __init__.py
│   └── settings.py  # Configuration management
└── utils/
    ├── __init__.py
    ├── colors.py    # Color utilities
    └── io.py        # I/O utilities
```

#### Use Pydantic for Data Validation
```python
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)

class ChatPayload(BaseModel):
    model: str
    messages: list[ChatMessage]
    search_domain_filter: list[str] | None = None
    search_recency_filter: str | None = None
```

---

## Medium Priority Improvements

### 5. Feature Enhancements

#### Add Conversation History
```python
# Save conversations to disk
class ConversationManager:
    def save_conversation(self, messages: list, filename: str):
        ...

    def load_conversation(self, filename: str) -> list:
        ...

    def list_conversations(self) -> list[str]:
        ...
```

#### Add Response Caching
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_cached_response(question_hash: str) -> str | None:
    ...
```

#### Export Functionality
```python
# Export search results and responses
def export_results(results: list, format: str = "json"):
    """
    Export to JSON, CSV, or Markdown
    """
    if format == "json":
        ...
    elif format == "markdown":
        ...
```

#### Add Retry Logic with Exponential Backoff
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def sendRequest(chat_payload: dict) -> str:
    ...
```

### 6. Testing Improvements

#### Add Integration Tests
```python
# tests/integration/test_api_integration.py
@pytest.mark.integration
def test_full_chat_flow():
    """Test complete chat workflow"""
    ...

@pytest.mark.integration
def test_model_switching():
    """Test switching between models"""
    ...
```

#### Add Coverage Reporting
```bash
# Add to pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=. --cov-report=html --cov-report=term"
```

#### Add Performance Tests
```python
import pytest
import time

def test_response_time():
    """Ensure responses are returned within acceptable time"""
    start = time.time()
    # ... make request
    duration = time.time() - start
    assert duration < 5.0  # 5 second timeout
```

### 7. Documentation Improvements

#### Add Docstrings
```python
def preparePayload(model: str, context: str, args: argparse.Namespace) -> dict:
    """
    Prepare the API request payload.

    Args:
        model: The AI model to use (e.g., "sonar", "sonar-pro")
        context: System context/prompt for the AI
        args: Parsed command-line arguments

    Returns:
        Dictionary containing the formatted API request payload

    Example:
        >>> args = argparse.Namespace(include=["example.com"])
        >>> payload = preparePayload("sonar", "helpful assistant", args)
    """
```

#### Add API Documentation
Create `docs/api.md` documenting all functions and their usage

#### Add Contributing Guide
Create `CONTRIBUTING.md` with:
- Code style guidelines
- How to run tests
- Pull request process

---

## Low Priority / Nice to Have

### 8. Developer Experience

#### Add Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
```

#### Add CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          uv sync
          uv run pytest
```

#### Add Makefile for Common Tasks
```makefile
.PHONY: test install lint format clean

test:
	uv run pytest tests/ -v

install:
	uv sync

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
```

### 9. User Experience

#### Add Progress Indicators
```python
from rich.progress import Progress, SpinnerColumn

with Progress(SpinnerColumn(), *Progress.get_default_columns()) as progress:
    task = progress.add_task("Thinking...", total=None)
    response = send_request(payload)
```

#### Add Color Themes
```python
THEMES = {
    "default": {...},
    "dark": {...},
    "light": {...},
    "solarized": {...}
}
```

#### Add Autocomplete for Shell
```bash
# Add shell completion for bash/zsh
# _hi_completion.sh
_hi_complete() {
    COMPREPLY=($(compgen -W "chat help update models" -- "${COMP_WORDS[1]}"))
}
complete -F _hi_complete hi
```

#### Better Error Messages
```python
class PerplexityError(Exception):
    """Base exception with helpful error messages"""

    def __init__(self, message: str, suggestion: str = ""):
        self.suggestion = suggestion
        super().__init__(message)

    def __str__(self):
        msg = super().__str__()
        if self.suggestion:
            msg += f"\n\nSuggestion: {self.suggestion}"
        return msg
```

### 10. Performance Optimizations

#### Add Async Support
```python
import asyncio
import httpx

async def sendRequestAsync(chat_payload: dict) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            CONST.API_URL,
            json=chat_payload,
            headers=CONST.HEADERS
        )
        return response.json()
```

#### Stream Large Responses
```python
def streamRequest(chat_payload: dict) -> Iterator[str]:
    """Stream response chunks as they arrive"""
    with requests.post(..., stream=True) as response:
        for chunk in response.iter_content(chunk_size=1024):
            yield chunk.decode()
```

---

## Installation & Deployment

### 11. Packaging Improvements

#### Publish to PyPI
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
hi = "perplexity_cli.__main__:main"
perplexity = "perplexity_cli.__main__:main"
```

Then users can install with:
```bash
pip install perplexity-cli
# or
uv tool install perplexity-cli
```

#### Add Docker Support
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
ENTRYPOINT ["hi"]
```

---

## Quick Wins (Can Implement Today)

1. Fix the color function bug in `hi_settings.py:10`
2. Add rich library to all print statements for better formatting
3. Add timeout to subprocess calls
4. Add `--version` flag
5. Add `--verbose` flag for debugging
6. Create `.env.example` file
7. Add more specific exception handling
8. Add stdin timeout to prevent hanging
9. Update README with better examples
10. Add cost estimation feature (track token usage)

---

## Modernization Suggestions

### Use Click Instead of Argparse
```python
import click

@click.command()
@click.argument('question', required=False)
@click.option('--model', '-m', default='sonar', help='Model to use')
@click.option('--context', '-c', help='System context')
def main(question, model, context):
    """Perplexity AI CLI - Ask questions and get AI-powered answers"""
    ...
```

### Use Rich for Better UI
```python
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

console.print(Panel("Welcome to Perplexity CLI", style="bold blue"))
console.print(Markdown(response_text))
```

### Add Prompt Toolkit for Better Input
```python
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

session = PromptSession(history=FileHistory('.hi_history'))
question = session.prompt('You: ')
```

---

## Summary of Immediate Actions

### Critical (Do First)
1. Fix `hi_settings.py:10` color function bug
2. Fix API key plaintext storage vulnerability
3. Add input validation
4. Fix typos in environment variable name

### High Priority (This Week)
5. Add type hints throughout
6. Implement proper logging
7. Add configuration file support
8. Reduce code duplication
9. Add retry logic with exponential backoff
10. Improve error messages

### Medium Priority (This Month)
11. Restructure project architecture
12. Add conversation history
13. Add integration tests
14. Publish to PyPI
15. Add CI/CD pipeline
