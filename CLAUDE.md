# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based CLI tool (`hi`) that provides command-line access to the Perplexity API (and optionally OpenAI). Users can ask questions, engage in chat sessions, and customize AI model selection and system prompts.

The main executable is `hi` - a Python script with a shebang that uses `uv run --script` for dependency management without requiring a virtual environment activation.

## Development Commands

### Running Tests
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_hi.py

# Run specific test function
uv run pytest tests/test_hi.py::test_pick_model -v

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov
```

### Installation & Setup
```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the tool system-wide (adds to PATH and sets API key)
bash ./install.sh YOUR_API_KEY

# Make hi executable
chmod +x hi

# Run directly (requires API key in environment)
export PERPLEXITY_API_KEY=your_key
./hi "your question"
```

### Running the Tool
```bash
# Single question
hi "What is the capital of France?"

# Chat mode
hi chat

# With specific model (0-4 or name)
hi "question" 2  # Uses sonar-reasoning

# Pipe input
cat code.py | hi "explain this code"

# Get help
hi help

# List models
hi models
```

## Architecture

### Core Files Structure

- **`hi`** (main executable): Entry point with CLI argument parsing and main loop
  - Uses `uv run --script` shebang for automatic dependency management
  - Contains chat loop, request handling, and response streaming logic
  - Implements both streaming (via OpenAI SDK) and non-streaming request modes

- **`hi_constants.py`**: Centralized configuration
  - API endpoints, available models, default context
  - Environment variable names (PERPLEXITY_API_KEY)
  - Color definitions for terminal output
  - Can be switched between Perplexity and OpenAI APIs (commented out code present)

- **`hi_help.py`**: User-facing help and model selection
  - `pick_model()`: Flexible model selection (by name, alias, or number)
  - `availableModels()`: Lists available Perplexity models
  - `color()`: Terminal color formatting (works with or without rich library)

- **`hi_settings.py`**: Installation and configuration management
  - `update_api_key()`: Validates and saves API key to shell config
  - `testApiKey()`: Validates API key by making test request
  - `update()`: Git pull for self-updating functionality
  - Writes to ~/.bashrc, ~/.zshrc, or ~/.cshrc depending on shell

### Request Flow

1. **CLI Parsing** (`hi:168-187`): argparse handles question, model, context, and search options
2. **Payload Preparation** (`hi:31-50`): Builds JSON payload with model, messages, search filters
3. **Request Handling**:
   - **Streaming mode** (`hi:95-131`): Uses OpenAI SDK client with stream=True
   - **Non-streaming** (`hi:85-93`): Direct requests.post() call
4. **Response Display**: Colored output with search results if available
5. **Chat Loop** (`hi:141-156`): Maintains conversation history, handles special commands

### Key Design Patterns

- **Dual API Support**: Code supports both Perplexity (active) and OpenAI (commented) by changing constants
- **Optional Dependencies**: Graceful fallback if `rich` or `openai` not available
- **Special Chat Commands**: "new chat", "change model", "exit" handled within conversation
- **Pipe Input Support** (`hi:159-166`): Can read from stdin for composability with other tools

### Test Architecture

- **Location**: `tests/test_hi.py` (pytest-based)
- **Module Loading**: Uses `importlib` to load the `hi` script as a module despite no .py extension
- **Mocking Strategy**: Patches `requests.post` and uses `MagicMock` for API responses
- **Test Categories**:
  - Environment variable configuration
  - API key validation (200/401 status codes)
  - Model selection (parametrized tests for all aliases)
  - Payload preparation with search filters

### Known Issues & Considerations

Review `FIXES_NEEDED.md` and `IMPROVEMENTS.md` for documented bugs and improvement suggestions. Key issues:
- Color function has duplicate implementations (hi_help.py and within hi script)
- API key stored in plaintext in shell configs
- Missing timeout handling on stdin.read() operations

## Development Notes

- **Python Version**: Requires Python 3.10 to <3.12
- **Package Manager**: Uses `uv` for dependency management (workspace with tests/ subdirectory)
- **API Key**: Must be set as `PERPLEXITY_API_KEY` environment variable
- **Git Workflow**: Main branch is `main`, CI runs pytest on push
- **CI/CD**: GitHub Actions workflow at `.github/workflows/main.yml` runs `uv run pytest`

### Available Models (as of codebase)
1. `sonar` (0, s, so, small)
2. `sonar-pro` (1, l, lo, long, pro)
3. `sonar-reasoning` (2, r, re, reson, reasoning)
4. `sonar-reasoning-pro` (3, rp, r-pro, rpro, reasoning-pro)
5. `sonar-deep-research` (4, d, deep)

### Important Environment Variables
- `PERPLEXITY_API_KEY`: Required for API access
- `HOME`: Used to locate shell config files for updates
