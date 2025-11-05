# Issues to Fix

This document tracks bugs, security vulnerabilities, and code quality issues that need to be addressed.

## Critical Issues (Fix Immediately)

### 1. API Key Exposure in Plaintext
**Location**: `install.sh:14,29,36,43`
**Severity**: CRITICAL
**Risk**: API key theft, unauthorized usage, billing fraud

**Problem**:
```bash
# CURRENT (INSECURE):
echo "export PERPLEXITY_API_KEY=$API_KEY" >> ~/.bashrc
```

The installation script writes API keys in plaintext to shell configuration files, creating multiple security risks:
- Keys visible in plaintext files
- Risk of accidental version control commits
- Keys exposed in backup files
- Visible to any process that can read shell configs

**Solution**:
Store API keys in a secure config file with restricted permissions (600) at `~/.config/perplexity/config`:

```bash
# Create secure config directory
CONFIG_DIR="$HOME/.config/perplexity"
CONFIG_FILE="$CONFIG_DIR/config"

mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

# Write API key to secure config file
echo "$API_KEY" > "$CONFIG_FILE"
chmod 600 "$CONFIG_FILE"
```

Update `hi_constants.py` to read from this location:
```python
def _load_api_key() -> str:
    """Load API key from secure config or environment."""
    # Try environment variable first
    env_key = os.getenv("PERPLEXITY_API_KEY")
    if env_key:
        return env_key

    # Try secure config file
    config_file = Path.home() / ".config" / "perplexity" / "config"
    if config_file.exists():
        return config_file.read_text().strip()

    return ""
```

---

### 2. Missing Input Validation
**Location**: `hi:52-83`
**Severity**: CRITICAL
**Risk**: API abuse, DoS, injection attacks, excessive costs

**Problem**:
User input is sent directly to the API without validation:
```python
question = input()  # No validation
chat_payload["messages"].append({"role": "user", "content": question})
```

This allows:
- Extremely long inputs causing DoS
- Control characters and null bytes
- Potential prompt injection attacks

**Solution**:
Add comprehensive input validation:
```python
import re

def validate_input(text: str, max_length: int = 10000) -> str:
    """
    Validate and sanitize user input.

    Raises:
        ValueError: If input is invalid
    """
    if not text or not text.strip():
        raise ValueError("Input cannot be empty")

    if len(text) > max_length:
        raise ValueError(f"Input too long (max {max_length} characters)")

    # Remove null bytes and control characters
    text = text.replace('\x00', '')
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)

    return text.strip()

def handleUserInput(chat_payload: dict, args: argparse.Namespace) -> str:
    if not args.single_use:
        question = input()

        if question and question not in ["exit", "new chat", "change model"]:
            try:
                question = validate_input(question)
            except ValueError as e:
                print(color(f"Error: {e}", "red"))
                return ""
        # ... rest of logic
```

---

### 3. No Security Tests
**Location**: `tests/test_hi.py`
**Severity**: CRITICAL
**Risk**: Undetected security vulnerabilities

**Problem**:
No tests verify input validation, injection attacks, or security edge cases.

**Solution**:
Create `tests/security/test_input_validation.py`:
```python
import pytest

def test_input_validation_null_bytes():
    """Test that null bytes are removed."""
    malicious_input = "test\x00DROP TABLE"
    cleaned = validate_input(malicious_input)
    assert '\x00' not in cleaned

def test_input_validation_length():
    """Test maximum length enforcement."""
    long_input = "a" * 10001
    with pytest.raises(ValueError, match="too long"):
        validate_input(long_input)

def test_input_validation_control_chars():
    """Test control character removal."""
    input_with_controls = "test\x01\x02\x03"
    cleaned = validate_input(input_with_controls)
    assert cleaned == "test"

def test_input_validation_empty():
    """Test empty input rejection."""
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_input("")
```

---

## High Priority Issues (Fix This Week)

### 4. Unsafe Subprocess Execution
**Location**: `hi_settings.py:69-75`
**Severity**: HIGH
**Risk**: Process hangs, command injection, poor error messages

**Problem**:
```python
directory: str = subprocess.run(
    ["dirname", subprocess.run(["which", "hi"], capture_output=True).stdout],
    capture_output=True,
    text=True,
).stdout.strip("\n")  # No timeout, nested calls
```

**Solution**:
```python
def update() -> None:
    """Update the hi command from git repository."""
    try:
        # First, find the hi command location
        which_result = subprocess.run(
            ["which", "hi"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )

        if not which_result.stdout.strip():
            print(color("Error: Could not find 'hi' command in PATH", "red"))
            exit(1)

        # Get the directory
        dirname_result = subprocess.run(
            ["dirname", which_result.stdout.strip()],
            capture_output=True,
            text=True,
            timeout=5,
            check=True
        )

        directory = dirname_result.stdout.strip()

        if not directory or directory == ".":
            print(color("Error: Invalid installation directory", "red"))
            exit(1)

        # Perform git pull
        subprocess.run(
            ["git", "pull", "-q"],
            cwd=directory,
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

        print(color("Update completed successfully", "green"))

    except subprocess.TimeoutExpired:
        print(color("Error: Command timed out", "red"))
        exit(1)
    except subprocess.CalledProcessError as e:
        print(color(f"Error: Update failed - {e}", "red"))
        exit(1)
```

---

### 5. Stdin Read Can Block Indefinitely
**Location**: `hi:159-166`
**Severity**: HIGH
**Risk**: CLI hangs with no feedback

**Problem**:
```python
def read_prompt(prompt: str = "") -> str:
    if not sys.stdin.isatty():
        stdin_prompt = sys.stdin.read().strip()  # Can hang forever
```

**Solution**:
```python
import select

def read_prompt(prompt: str = "", timeout: int = 60) -> str:
    """Read prompt from stdin with timeout."""
    if not sys.stdin.isatty():
        # Check if stdin has data available
        if select.select([sys.stdin], [], [], timeout)[0]:
            stdin_prompt = sys.stdin.read().strip()
            if prompt:
                return f"{prompt}\n````\n{stdin_prompt}\n````"
            elif stdin_prompt:
                return stdin_prompt
        else:
            print(color("Warning: Stdin read timeout, using prompt only", "yellow"))

    return prompt
```

---

### 6. Poor Error Handling in sendRequest
**Location**: `hi:85-93`
**Severity**: HIGH
**Risk**: Poor UX, unclear error messages

**Problem**:
```python
except requests.exceptions.RequestException as e:
    print(color(f"Error: {e}", "red"))
    exit()  # Generic error, no exit code
```

**Solution**:
Apply the same comprehensive error handling from `streamRequest`:
```python
def sendRequest(chat_payload: dict) -> str:
    try:
        response = requests.post(
            CONST.API_URL,
            json=chat_payload,
            headers=CONST.HEADERS,
            timeout=CONST.TIMEOUT,
            verify=True
        )
        response.raise_for_status()
        displayResponse(response)
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        print(color("Error: Request timed out. Please try again.", "red"))
        exit(1)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(color("Error: Invalid API key.", "red"))
        elif e.response.status_code == 429:
            print(color("Error: Rate limit exceeded.", "red"))
        else:
            print(color(f"Error: HTTP {e.response.status_code}", "red"))
        exit(1)
    except requests.exceptions.ConnectionError:
        print(color("Error: Cannot connect to API.", "red"))
        exit(1)
```

---

### 7. Duplicate Color Function
**Location**: `hi_help.py:12-17` and `hi:12` (import from hi_help)
**Severity**: HIGH
**Risk**: Code duplication, maintenance burden

**Problem**:
The `color()` function logic exists in multiple places, leading to inconsistency.

**Solution**:
Move to `hi_constants.py`:
```python
# hi_constants.py
import sys

def color(text: str, color_name: str) -> str:
    """Format text with color using rich or ANSI codes."""
    if 'rich' in sys.modules:
        return f"[{color_name}]{text}[/]"

    if color_name not in COLORS:
        return text

    return f"{COLORS[color_name]}{text}{COLORS['reset']}"
```

Then import everywhere:
```python
from hi_constants import color
```

---

### 8. Missing Type Hints
**Location**: All Python files
**Severity**: HIGH
**Risk**: Poor code maintainability, unclear interfaces

**Problem**:
Most functions lack proper type hints.

**Solution**:
Add comprehensive type hints:
```python
from typing import Optional, List, Dict, Any

def printSearchResults(search_results: Optional[List[Dict[str, str]]]) -> None:
    """Print search results with proper formatting."""
    ...

def preparePayload(
    model: str = CONST.AVAILABLE_MODELS[0],
    context: str = CONST.DEFAULT_CONTEXT,
    args: argparse.Namespace = argparse.Namespace()
) -> Dict[str, Any]:
    """Prepare API request payload."""
    ...

def handleUserInput(
    chat_payload: Dict[str, Any],
    args: argparse.Namespace
) -> str:
    """Handle user input in chat or single-use mode."""
    ...
```

---

### 9. No Integration Tests
**Location**: `tests/test_hi.py`
**Severity**: HIGH
**Risk**: Integration issues not caught before deployment

**Problem**:
All tests are unit tests with mocks. No integration tests verify actual API interaction.

**Solution**:
Create `tests/integration/test_api_integration.py`:
```python
import pytest
import os

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("PERPLEXITY_API_KEY"),
    reason="API key not available"
)
def test_real_api_call():
    """Test actual API call with real key."""
    # Make real API call to verify integration
    pass

@pytest.mark.integration
def test_model_selection_integration():
    """Test model selection with API."""
    pass
```

---

### 10. No Error Handling Tests
**Location**: `tests/test_hi.py`
**Severity**: HIGH
**Risk**: Error paths not tested

**Problem**:
Tests don't verify error handling works correctly.

**Solution**:
Add error handling tests:
```python
def test_api_timeout_handling():
    """Verify timeout errors are handled gracefully."""
    with patch('requests.post', side_effect=requests.exceptions.Timeout):
        with pytest.raises(SystemExit) as exc:
            sendRequest({})
        assert exc.value.code == 1

def test_network_error_handling():
    """Verify network errors are handled."""
    with patch('requests.post', side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(SystemExit):
            sendRequest({})
```

---

## Medium Priority Issues (Fix This Month)

### 11. Unvalidated Shell Script Input
**Location**: `install.sh:14,27,34,41`
**Severity**: MEDIUM
**Risk**: Command injection via API key argument

**Problem**:
```bash
API_KEY=$1
echo "export PERPLEXITY_API_KEY=$API_KEY" >> ~/.bashrc
```

**Solution**:
```bash
API_KEY="$1"

# Validate API key format
if ! echo "$API_KEY" | grep -qE '^pplx-[a-zA-Z0-9_-]+$'; then
    echo "Error: Invalid API key format"
    exit 1
fi
```

---

### 12. No Response Validation
**Location**: `hi:90,110`
**Severity**: MEDIUM
**Risk**: KeyError/AttributeError on malformed responses

**Problem**:
```python
response.json()["choices"][0]["message"]["content"]  # Could KeyError
```

**Solution**:
```python
def extract_response_content(response_data: dict) -> str:
    """Safely extract content from API response."""
    try:
        choices = response_data.get("choices", [])
        if not choices:
            raise ValueError("No choices in response")

        message = choices[0].get("message", {})
        content = message.get("content")

        if content is None:
            raise ValueError("No content in message")

        return content
    except (KeyError, IndexError, AttributeError) as e:
        raise ValueError(f"Invalid response structure: {e}")
```

---

### 13. Broad Exception Handling
**Location**: `hi_settings.py:56-63`
**Severity**: MEDIUM
**Risk**: Difficult debugging

**Problem**:
```python
except Exception as e:
    print(color(f"Failed to accept API key: {e}...", "red"))
    exit(1)
```

**Solution**:
Use specific exception types:
```python
except ValueError as e:
    print(color(f"Validation error: {e}", "red"))
    exit(1)
except EnvironmentError as e:
    print(color(f"Environment error: {e}", "red"))
    exit(1)
except IOError as e:
    print(color(f"File error: {e}", "red"))
    exit(1)
```

---

### 14. Magic Strings Throughout Code
**Location**: All Python files
**Severity**: MEDIUM
**Risk**: Typos, maintenance issues

**Problem**:
Hardcoded strings like "exit", "chat", "new chat" scattered throughout.

**Solution**:
```python
# hi_constants.py
class Commands:
    """CLI commands."""
    EXIT = "exit"
    CHAT = "chat"
    NEW_CHAT = "new chat"
    CHANGE_MODEL = "change model"
    HELP = "help"
    MODELS = "models"
    UPDATE = "update"

class ExitCodes:
    """Exit codes."""
    SUCCESS = 0
    API_ERROR = 1
    CONFIG_ERROR = 2
    INPUT_ERROR = 3
    NETWORK_ERROR = 4
```

---

### 15. No Logging Framework
**Location**: All Python files
**Severity**: MEDIUM
**Risk**: Difficult debugging

**Problem**:
Using `print()` statements instead of proper logging.

**Solution**:
```python
import logging
from pathlib import Path

log_dir = Path.home() / ".local" / "share" / "perplexity"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "perplexity.log"),
    ]
)
logger = logging.getLogger(__name__)
```

---

### 16. Race Condition in Chat Loop
**Location**: `hi:141-156`
**Severity**: MEDIUM
**Risk**: Unpredictable behavior

**Problem**:
```python
while args.question != "exit":
    args.question = handleUserInput(chat_payload, args)  # Modifying args
```

**Solution**:
```python
def chat_loop(model: str, context: str, args: argparse.Namespace) -> None:
    chat_payload = preparePayload(model, context, args)

    while True:
        question = handleUserInput(chat_payload, args)

        if question == Commands.EXIT:
            break

        if not question:
            continue

        # ... rest of logic
```

---

### 17. Stream Response Wrong Exception Types
**Location**: `hi:115-131`
**Severity**: MEDIUM
**Risk**: Exceptions not caught

**Problem**:
```python
except requests.exceptions.Timeout:  # Won't catch OpenAI timeout
```

**Solution**:
```python
from openai import OpenAIError, APITimeoutError, APIConnectionError

except APITimeoutError:
    print(color("Error: Request timed out.", "red"))
    exit(1)
except APIConnectionError:
    print(color("Error: Cannot connect to API.", "red"))
    exit(1)
except OpenAIError as e:
    print(color(f"Error: API error - {e}", "red"))
    exit(1)
```

---

### 18. Potential None Dereference
**Location**: `hi:110-111`
**Severity**: MEDIUM
**Risk**: AttributeError

**Problem**:
```python
response_message += response.choices[0].delta.content  # Could be None
```

**Solution**:
```python
delta_content = response.choices[0].delta.content
if delta_content:
    response_message += delta_content
    print(delta_content, end="", flush=True)
```

---

### 19. Missing HTTPS Verification
**Location**: `hi:87,100`
**Severity**: MEDIUM
**Risk**: MITM attacks

**Problem**:
No explicit SSL certificate verification.

**Solution**:
```python
response = requests.post(
    CONST.API_URL,
    json=chat_payload,
    headers=CONST.HEADERS,
    timeout=CONST.TIMEOUT,
    verify=True  # Explicitly enable
)
```

---

### 20. API Key in Global Headers
**Location**: `hi_constants.py:32-36`
**Severity**: MEDIUM
**Risk**: Accidental logging

**Problem**:
```python
HEADERS = {
    "authorization": f"Bearer {API_KEY}",  # Could be logged
}
```

**Solution**:
```python
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
}

def get_headers() -> dict:
    """Get headers with API key."""
    return {
        **HEADERS,
        "authorization": f"Bearer {API_KEY}"
    }
```

---

## Low Priority Issues (Nice to Have)

### 21. Excessive Timeout Value
**Location**: `hi_constants.py:37`
**Severity**: LOW
**Risk**: Users wait too long for failures

**Problem**:
```python
TIMEOUT = 7200  # 2 hours is excessive
```

**Solution**:
```python
TIMEOUT_CONNECT = 10  # 10 seconds to connect
TIMEOUT_READ = 300    # 5 minutes to read
TIMEOUT = (TIMEOUT_CONNECT, TIMEOUT_READ)
```

---

### 22. Inconsistent Exit Codes
**Location**: All Python files
**Severity**: LOW
**Risk**: Scripts can't differentiate error types

**Problem**:
Mix of `exit()`, `exit(1)`, `exit(0)`.

**Solution**:
Use ExitCodes class consistently (see issue #14).

---

### 23. Empty Response Handling
**Location**: `hi:25-29`
**Severity**: LOW
**Risk**: Poor UX

**Problem**:
```python
def printSearchResults(search_results) -> None:
    if search_results is not None:
        # Doesn't distinguish empty vs None
```

**Solution**:
```python
def printSearchResults(search_results: Optional[List[Dict[str, str]]]) -> None:
    if search_results is None:
        return

    if not search_results:
        print(color("No search results available", "yellow"))
        return

    # ... print results
```

---

## Summary Statistics

| Priority | Count | % of Total |
|----------|-------|-----------|
| Critical | 3     | 13%       |
| High     | 7     | 30%       |
| Medium   | 10    | 44%       |
| Low      | 3     | 13%       |
| **Total**| **23**| **100%**  |

## Recommended Fix Order

1. Fix API key plaintext storage (Critical)
2. Add input validation (Critical)
3. Add security tests (Critical)
4. Fix subprocess execution (High)
5. Fix stdin blocking (High)
6. Improve error handling (High)
7. Remove duplicate code (High)
8. Add type hints (High)
9. Add integration tests (High)
10. Add error handling tests (High)
11. Continue with Medium priority items
12. Address Low priority items as time permits
