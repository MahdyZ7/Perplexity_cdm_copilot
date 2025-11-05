# Specific Code Fixes Needed

## Critical Bug Fixes

### 1. Color Function Bug (hi_settings.py:10)
```python
# CURRENT (BROKEN):
def color(text, color) -> str:
    if "rich" in sys.modules:
        return f"[{color}]{text}\033"  # ❌ Wrong closing tag
    return text

# FIX TO:
def color(text, color) -> str:
    if "rich" in sys.modules:
        return f"[{color}]{text}[/]"  # ✅ Correct rich markup
    return text
```

### 2. Code Duplication - Remove Duplicate Color Function
The `color()` function exists in both:
- `hi:27-32`
- `hi_settings.py:8-11`

**Solution**: Move to `hi_constants.py` and import it in both places:

```python
# hi_constants.py
import sys

def color(text: str, color_name: str) -> str:
    """
    Format text with color using rich or ANSI codes.

    Args:
        text: The text to colorize
        color_name: Color name (e.g., 'red', 'blue', 'green')

    Returns:
        Formatted string with color codes
    """
    if 'rich' in sys.modules:
        return f"[{color_name}]{text}[/]"
    if color_name not in COLORS:
        return text
    return f"{COLORS[color_name]}{text}{COLORS['reset']}"
```

### 3. Missing Timeout Handling (hi:161)
```python
# CURRENT:
def read_prompt(prompt: str = "") -> str:
    if not sys.stdin.isatty():
        stdin_prompt = sys.stdin.read().strip()  # ❌ Can block forever
        ...

# FIX TO:
import signal

def read_prompt(prompt: str = "", timeout: int = 60) -> str:
    """Read prompt with timeout to prevent hanging."""
    if not sys.stdin.isatty():
        def timeout_handler(signum, frame):
            raise TimeoutError("Stdin read timeout")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        try:
            stdin_prompt = sys.stdin.read().strip()
            signal.alarm(0)  # Cancel alarm
        except TimeoutError:
            print("Input timeout - using prompt only")
            return prompt
        ...
```

### 4. Missing Error Handling (hi:101-107)
```python
# CURRENT:
def sendRequest(chat_payload: dict) -> str:
    try:
        response = requests.post(CONST.API_URL, json=chat_payload,
                                headers=CONST.HEADERS, timeout=CONST.TIMEOUT)
        response.raise_for_status()
        # ... ❌ Generic exception catching
    except requests.exceptions.RequestException as e:
        print(color(f"Error: {e}", "red"))
        exit()

# FIX TO:
def sendRequest(chat_payload: dict) -> str:
    """Send request with proper error handling."""
    try:
        response = requests.post(
            CONST.API_URL,
            json=chat_payload,
            headers=CONST.HEADERS,
            timeout=CONST.TIMEOUT
        )
        response.raise_for_status()
        displayResponse(response)
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        print(color("Error: Request timed out. Please try again.", "red"))
        exit(1)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(color("Error: Invalid API key. Please check your credentials.", "red"))
        elif e.response.status_code == 429:
            print(color("Error: Rate limit exceeded. Please wait and try again.", "red"))
        else:
            print(color(f"Error: HTTP {e.response.status_code} - {e}", "red"))
        exit(1)

    except requests.exceptions.ConnectionError:
        print(color("Error: Cannot connect to API. Check your internet connection.", "red"))
        exit(1)

    except (KeyError, IndexError) as e:
        print(color(f"Error: Unexpected API response format: {e}", "red"))
        exit(1)
```

### 5. Unsafe Subprocess Call (hi_settings.py:70-74)
```python
# CURRENT:
directory: str = subprocess.run(
    ["dirname", subprocess.run(["which", "hi"], capture_output=True).stdout],
    capture_output=True,
    text=True,
).stdout.strip("\n")  # ❌ No timeout, nested subprocess

# FIX TO:
try:
    which_result = subprocess.run(
        ["which", "hi"],
        capture_output=True,
        text=True,
        timeout=5,
        check=True
    )
    directory = subprocess.run(
        ["dirname", which_result.stdout],
        capture_output=True,
        text=True,
        timeout=5,
        check=True
    ).stdout.strip()
except subprocess.TimeoutExpired:
    print(color("Error: Command timeout", "red"))
    exit(1)
except subprocess.CalledProcessError as e:
    print(color(f"Error: Command failed: {e}", "red"))
    exit(1)
```

## Security Improvements

### 6. Secure API Key Storage (install.sh:14-39)
```bash
# CURRENT: Writes to shell config files ❌

# BETTER APPROACH: Create config directory
#!/bin/sh
set -o errexit

if [ $# -eq 0 ]; then
    echo 'Add the perplexity API key as an argument'
    exit 0
fi

chmod +x hi
API_KEY=$1
current_dir=$(pwd)

# Create config directory
CONFIG_DIR="$HOME/.config/perplexity"
CONFIG_FILE="$CONFIG_DIR/config.toml"

mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

# Write config file
cat > "$CONFIG_FILE" << EOF
[api]
key = "$API_KEY"
timeout = 7200

[defaults]
model = "sonar"
EOF

chmod 600 "$CONFIG_FILE"

# Add to PATH only
if [ -f ~/.bashrc ]; then
    echo "export PATH=\$PATH:$current_dir" >> ~/.bashrc
fi
if [ -f ~/.zshrc ]; then
    echo "export PATH=\$PATH:$current_dir" >> ~/.zshrc
fi

echo "✓ Configuration saved to $CONFIG_FILE"
echo "✓ Added to PATH"
```

### 7. Input Validation (Add to hi before API calls)
```python
def validate_input(text: str, max_length: int = 10000) -> str:
    """
    Validate and sanitize user input.

    Args:
        text: User input to validate
        max_length: Maximum allowed length

    Returns:
        Sanitized input string

    Raises:
        ValueError: If input is invalid
    """
    if not text or not text.strip():
        raise ValueError("Input cannot be empty")

    if len(text) > max_length:
        raise ValueError(f"Input too long (max {max_length} characters)")

    # Remove any null bytes
    text = text.replace('\x00', '')

    return text.strip()

# Use in handleUserInput:
def handleUserInput(chat_payload: dict, args: argparse.Namespace) -> str:
    # ... existing code ...
    if question:
        try:
            question = validate_input(question)
        except ValueError as e:
            print(color(f"Error: {e}", "red"))
            return ""

        chat_payload["messages"].append({
            "role": "user",
            "content": question
        })
    return question
```

## Code Quality Improvements

### 8. Add Type Hints Throughout
```python
# Example for hi_help.py with complete type hints:
from typing import Optional

def availableModels() -> str:
    """Return formatted string of available models."""
    models = "\t Available models:\n"
    for i in range(len(CONST.AVAILABLE_MODELS)):
        models += f"		[{i}] - {CONST.AVAILABLE_MODELS[i]}\n"
    return models

def pick_model(model: Optional[str]) -> str:
    """
    Select a model based on user input.

    Args:
        model: Model name or shorthand

    Returns:
        Full model name from AVAILABLE_MODELS
    """
    default_model: str = CONST.DEFAULT_MODEL
    if not model:
        return default_model
    # ... rest of function
```

### 9. Replace Magic Strings/Numbers
```python
# CURRENT: Magic strings throughout code
if question == "exit":
    exit()
if question.lower() == "help":
    ...

# FIX TO: Define constants
# hi_constants.py
COMMANDS = {
    "EXIT": "exit",
    "HELP": "help",
    "MODELS": "models",
    "UPDATE": "update",
    "CHAT": "chat",
    "NEW_CHAT": "new chat",
    "CHANGE_MODEL": "change model",
}

EXIT_CODES = {
    "SUCCESS": 0,
    "API_ERROR": 1,
    "CONFIG_ERROR": 2,
    "INPUT_ERROR": 3,
}

# Then use:
if question == COMMANDS["EXIT"]:
    exit(EXIT_CODES["SUCCESS"])
```

### 10. Add Logging
```python
# At top of hi file:
import logging
from pathlib import Path

# Setup logging
log_dir = Path.home() / ".local" / "share" / "perplexity"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "perplexity.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Replace print statements:
# OLD: print(f"Error: {e}")
# NEW: logger.error(f"API request failed: {e}")

# OLD: print("Updating hi")
# NEW: logger.info("Starting update process")
```

## Configuration File Support

### 11. Add Config File Reader
```python
# hi_config.py (new file)
from pathlib import Path
from typing import Optional
import tomli  # Add to dependencies

class Config:
    """Configuration management for Perplexity CLI."""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "perplexity"
        self.config_file = self.config_dir / "config.toml"
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if not self.config_file.exists():
            return self._get_defaults()

        try:
            with open(self.config_file, "rb") as f:
                return tomli.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
            return self._get_defaults()

    def _get_defaults(self) -> dict:
        """Get default configuration."""
        return {
            "api": {
                "key": os.getenv("PERPLEXITY_API_KEY", ""),
                "timeout": 7200,
            },
            "defaults": {
                "model": "sonar",
                "context": CONST.DEFAULT_CONTEXT,
            },
            "display": {
                "colors": True,
            }
        }

    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get configuration value."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default

    @property
    def api_key(self) -> str:
        """Get API key from config or environment."""
        return self.get("api.key") or os.getenv("PERPLEXITY_API_KEY", "")

# Usage in hi:
config = Config()
CONST.API_KEY = config.api_key
```

## Summary of File Changes Needed

| File | Lines | Issue | Priority |
|------|-------|-------|----------|
| hi_settings.py | 10 | Color function bug | 🔴 Critical |
| hi | 27-32 | Duplicate color function | 🟡 High |
| hi | 161 | Missing stdin timeout | 🟡 High |
| hi | 101-107 | Poor error handling | 🟡 High |
| hi_settings.py | 70-74 | Unsafe subprocess | 🟡 High |
| install.sh | 14-39 | Insecure key storage | 🔴 Critical |
| hi | 66-97 | Missing input validation | 🔴 Critical |
| All files | - | Missing type hints | 🟡 High |
| All files | - | Using print vs logging | 🟡 High |
| README.md | 45,107 | Typo: PERPLIXITY | 🟢 Medium |
