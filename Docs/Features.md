# Feature Requests and Improvements

This document outlines suggested new features, enhancements, and quality-of-life improvements for the Perplexity CLI tool.

## High Priority Features

### 1. Configuration File Support
**Priority**: HIGH
**Effort**: Medium

**Description**:
Add support for a configuration file to store user preferences instead of relying solely on environment variables and command-line arguments.

**Benefits**:
- Persistent user preferences
- Easier model/context switching
- Better security for API keys
- Multiple profile support

**Implementation**:
```python
# ~/.config/perplexity/config.toml
[default]
api_key = "pplx-xxx"  # Read from secure file with 600 permissions
default_model = "sonar-pro"
default_context = "You are a helpful assistant"
timeout = 300

[profiles]
[profiles.coding]
model = "sonar-reasoning"
context = "You are an expert programmer"

[profiles.research]
model = "sonar-deep-research"
context = "You are a research assistant"
```

Usage:
```bash
hi --profile coding "explain recursion"
```

Code structure:
```python
# config.py
import tomli
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    api_key: str
    default_model: str
    default_context: str
    timeout: int
    profiles: dict

def load_config() -> Config:
    """Load configuration from file."""
    config_file = Path.home() / ".config" / "perplexity" / "config.toml"
    if config_file.exists():
        with open(config_file, "rb") as f:
            data = tomli.load(f)
            return Config(**data["default"], profiles=data.get("profiles", {}))
    return Config.default()
```

---

### 2. History and Session Management
**Priority**: HIGH
**Effort**: Medium

**Description**:
Save conversation history and allow users to resume previous sessions.

**Benefits**:
- Resume conversations across terminal sessions
- Review past interactions
- Export conversations for documentation
- Search through history

**Implementation**:
```python
# history.py
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class ChatHistory:
    def __init__(self):
        self.history_dir = Path.home() / ".local" / "share" / "perplexity" / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def save_message(self, session_id: str, role: str, content: str):
        """Save a message to history."""
        session_file = self.history_dir / f"{session_id}.json"

        history = []
        if session_file.exists():
            history = json.loads(session_file.read_text())

        history.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        })

        session_file.write_text(json.dumps(history, indent=2))

    def get_session(self, session_id: str) -> List[Dict]:
        """Load a previous session."""
        session_file = self.history_dir / f"{session_id}.json"
        if session_file.exists():
            return json.loads(session_file.read_text())
        return []

    def list_sessions(self) -> List[str]:
        """List all saved sessions."""
        return [f.stem for f in self.history_dir.glob("*.json")]
```

Commands:
```bash
# List previous sessions
hi history

# Resume a session
hi resume <session_id>

# Export session
hi export <session_id> -o conversation.md

# Search history
hi search "docker commands"
```

---

### 3. Streaming Progress Indicator
**Priority**: HIGH
**Effort**: Low

**Description**:
Add a visual progress indicator while waiting for API responses, especially for slower models.

**Benefits**:
- Better user feedback
- Shows the tool is working
- Reduces perceived wait time

**Implementation**:
```python
from rich.console import Console
from rich.spinner import Spinner

console = Console()

def streamRequest(chat_payload: dict) -> str:
    try:
        response_message = ""
        first_response = True
        client = OpenAI(api_key=CONST.API_KEY, base_url=CONST.API_URL_BASE)

        # Show spinner while waiting for first response
        with console.status("[bold cyan]Thinking...", spinner="dots"):
            response_stream = client.chat.completions.create(
                model=chat_payload["model"],
                messages=chat_payload["messages"],
                stream=True
            )

            print(color(f"{chat_payload['model']}: ", "purple"), end="")
            for response in response_stream:
                if first_response:
                    first_response = False
                    # Stop spinner, start printing

                delta_content = response.choices[0].delta.content
                if delta_content:
                    response_message += delta_content
                    print(delta_content, end="", flush=True)

        print()
        return response_message
    except Exception as e:
        # error handling
        pass
```

---

### 4. Cost Tracking
**Priority**: HIGH
**Effort**: Medium

**Description**:
Track API usage and estimated costs to help users manage their spending.

**Benefits**:
- Transparency in API costs
- Budget management
- Usage insights

**Implementation**:
```python
# cost_tracker.py
from pathlib import Path
import json
from datetime import datetime

class CostTracker:
    # Perplexity pricing (as of implementation)
    PRICING = {
        "sonar": {"per_1k": 0.0005},
        "sonar-pro": {"per_1k": 0.003},
        "sonar-reasoning": {"per_1k": 0.001},
        "sonar-reasoning-pro": {"per_1k": 0.005},
        "sonar-deep-research": {"per_1k": 0.005},
    }

    def __init__(self):
        self.usage_file = Path.home() / ".local" / "share" / "perplexity" / "usage.json"
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)

    def log_request(self, model: str, prompt_tokens: int, completion_tokens: int):
        """Log a request and calculate cost."""
        cost = self._calculate_cost(model, prompt_tokens, completion_tokens)

        usage = self._load_usage()
        usage.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost": cost
        })

        self.usage_file.write_text(json.dumps(usage, indent=2))

    def get_summary(self, days: int = 30) -> dict:
        """Get usage summary for the past N days."""
        usage = self._load_usage()
        # Filter and summarize
        return {
            "total_requests": len(usage),
            "total_cost": sum(u["cost"] for u in usage),
            "by_model": {}  # Group by model
        }
```

Commands:
```bash
# Show usage summary
hi usage

# Show detailed breakdown
hi usage --detailed

# Show costs for specific time period
hi usage --days 7
```

---

### 5. Better Error Messages with Suggestions
**Priority**: HIGH
**Effort**: Low

**Description**:
Improve error messages to include helpful suggestions and common solutions.

**Implementation**:
```python
class ErrorHandler:
    """Centralized error handling with helpful suggestions."""

    @staticmethod
    def handle_api_error(error: Exception, context: dict = None):
        """Handle API errors with context-aware suggestions."""
        if isinstance(error, requests.exceptions.Timeout):
            print(color("⚠ Error: Request timed out", "red"))
            print(color("Suggestions:", "yellow"))
            print("  • Try using a faster model (sonar instead of sonar-pro)")
            print("  • Check your internet connection")
            print("  • Reduce the length of your prompt")

        elif isinstance(error, requests.exceptions.HTTPError):
            status = error.response.status_code

            if status == 401:
                print(color("⚠ Error: Invalid API key", "red"))
                print(color("Suggestions:", "yellow"))
                print("  • Verify your key at https://www.perplexity.ai/settings/api")
                print("  • Run: hi --configure to set a new key")
                print(f"  • Check environment variable: echo $PERPLEXITY_API_KEY")

            elif status == 429:
                print(color("⚠ Error: Rate limit exceeded", "red"))
                print(color("Suggestions:", "yellow"))
                print("  • Wait a few moments before trying again")
                print("  • Check your usage at Perplexity dashboard")
                print("  • Consider upgrading your plan")

            elif status == 402:
                print(color("⚠ Error: Payment required", "red"))
                print(color("Suggestions:", "yellow"))
                print("  • Add credits at https://www.perplexity.ai/settings/api")
                print("  • Check your current balance and usage")
```

---

### 6. Multi-Language Support
**Priority**: MEDIUM
**Effort**: High

**Description**:
Add support for internationalization (i18n) to make the tool accessible to non-English speakers.

**Implementation**:
```python
# i18n.py
import gettext
from pathlib import Path

def setup_i18n(language: str = None):
    """Setup internationalization."""
    locale_dir = Path(__file__).parent / "locales"

    # Auto-detect if not specified
    if language is None:
        import locale
        language = locale.getdefaultlocale()[0][:2]

    try:
        translation = gettext.translation('hi', locale_dir, languages=[language])
        translation.install()
    except FileNotFoundError:
        # Fall back to English
        gettext.install('hi')

# Usage in code:
print(_("Error: Invalid API key"))
```

Supported languages could include:
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)

---

## Medium Priority Features

### 7. Plugin System
**Priority**: MEDIUM
**Effort**: High

**Description**:
Add a plugin system to allow users to extend functionality without modifying core code.

**Example Plugins**:
- Syntax highlighting for code responses
- Automatic code execution in sandboxed environment
- Integration with external tools (jira, github, etc.)
- Custom output formatters (PDF, HTML, etc.)

**Implementation**:
```python
# plugins/base.py
from abc import ABC, abstractmethod

class Plugin(ABC):
    """Base class for plugins."""

    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @abstractmethod
    def on_request(self, payload: dict) -> dict:
        """Called before API request."""
        return payload

    @abstractmethod
    def on_response(self, response: str) -> str:
        """Called after API response."""
        return response

# plugins/syntax_highlighter.py
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

class SyntaxHighlighter(Plugin):
    def name(self) -> str:
        return "syntax_highlighter"

    def on_response(self, response: str) -> str:
        """Highlight code blocks in response."""
        # Parse markdown code blocks and apply syntax highlighting
        return highlighted_response
```

---

### 8. Template System for Common Prompts
**Priority**: MEDIUM
**Effort**: Low

**Description**:
Allow users to save and reuse prompt templates.

**Implementation**:
```bash
# Save a template
hi template save code-review "Review this code for bugs and improvements: {code}"

# Use a template
cat file.py | hi template use code-review

# List templates
hi template list

# Delete template
hi template delete code-review
```

Templates file structure:
```json
{
  "code-review": {
    "template": "Review this code for bugs and improvements: {code}",
    "model": "sonar-reasoning",
    "context": "You are an expert code reviewer"
  },
  "explain": {
    "template": "Explain the following concept in simple terms: {concept}",
    "model": "sonar-pro"
  }
}
```

---

### 9. Batch Processing
**Priority**: MEDIUM
**Effort**: Medium

**Description**:
Process multiple files or questions in batch mode with progress tracking.

**Usage**:
```bash
# Process multiple files
hi batch -f file1.py file2.py file3.py --prompt "Summarize this code"

# Process from a list
cat questions.txt | hi batch --output results/

# With parallel processing
hi batch -f *.py --parallel 3 --prompt "Find bugs in this code"
```

**Implementation**:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress

def batch_process(files: List[Path], prompt: str, parallel: int = 1):
    """Process multiple files in batch."""
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing...", total=len(files))

        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {}

            for file in files:
                content = file.read_text()
                full_prompt = f"{prompt}\n\n{content}"
                future = executor.submit(send_request, full_prompt)
                futures[future] = file

            for future in as_completed(futures):
                file = futures[future]
                try:
                    result = future.result()
                    save_result(file, result)
                except Exception as e:
                    logger.error(f"Error processing {file}: {e}")

                progress.update(task, advance=1)
```

---

### 10. Web Search Citations
**Priority**: MEDIUM
**Effort**: Low

**Description**:
Improve search results display with better formatting and citation management.

**Current**:
```
[1] Title - URL - Date
```

**Improved**:
```
╭─ Search Results (3 sources) ─────────────────────────────╮
│ [1] Understanding Python Decorators                      │
│     https://realpython.com/python-decorators/            │
│     Published: 2024-01-15 • Relevance: ★★★★☆            │
│                                                           │
│ [2] Advanced Decorator Patterns                          │
│     https://docs.python.org/3/howto/decorator-library.html│
│     Updated: 2024-02-01 • Relevance: ★★★★★              │
╰───────────────────────────────────────────────────────────╯
```

**Implementation**:
```python
from rich.table import Table
from rich.console import Console

def printSearchResults(search_results: List[Dict[str, str]]) -> None:
    """Print formatted search results."""
    if not search_results:
        return

    console = Console()
    table = Table(title="Search Results", show_header=True)

    table.add_column("#", style="cyan", width=3)
    table.add_column("Title", style="white")
    table.add_column("Source", style="blue")
    table.add_column("Date", style="yellow")

    for idx, result in enumerate(search_results, 1):
        table.add_row(
            str(idx),
            result.get('title', 'No Title'),
            result.get('url', 'No URL'),
            result.get('date', 'No Date')
        )

    console.print(table)
```

---

### 11. Conversation Branching
**Priority**: MEDIUM
**Effort**: High

**Description**:
Allow users to branch conversations to explore different directions without losing context.

**Usage**:
```bash
# In chat mode:
You: Explain quantum computing
AI: [Response about quantum computing]

You: /branch classical
You: Now explain classical computing
AI: [Response about classical computing]

You: /switch main
You: Tell me more about quantum gates
AI: [Continues from quantum computing branch]

You: /branches
Branches:
  * main (current)
  - classical
```

---

### 12. Output Formatters
**Priority**: MEDIUM
**Effort**: Medium

**Description**:
Add support for different output formats beyond plain text.

**Formats**:
- Markdown
- JSON
- HTML
- PDF (requires additional dependencies)
- LaTeX

**Usage**:
```bash
# Export as markdown
hi "Explain Python" --format markdown -o explanation.md

# Export as HTML
hi "Tutorial on Docker" --format html -o tutorial.html

# JSON for programmatic use
hi "List top 5 Python frameworks" --format json
```

**Implementation**:
```python
from abc import ABC, abstractmethod

class OutputFormatter(ABC):
    @abstractmethod
    def format(self, response: str, metadata: dict) -> str:
        pass

class MarkdownFormatter(OutputFormatter):
    def format(self, response: str, metadata: dict) -> str:
        return f"""# {metadata['model']} Response
**Date**: {metadata['timestamp']}
**Model**: {metadata['model']}

{response}

## Sources
{self._format_sources(metadata['sources'])}
"""

class JSONFormatter(OutputFormatter):
    def format(self, response: str, metadata: dict) -> str:
        return json.dumps({
            "response": response,
            "metadata": metadata
        }, indent=2)
```

---

### 13. Keyboard Shortcuts in Chat Mode
**Priority**: MEDIUM
**Effort**: Low

**Description**:
Add keyboard shortcuts for common actions in chat mode.

**Shortcuts**:
- `Ctrl+C`: Cancel current request
- `Ctrl+D`: Exit chat
- `Ctrl+L`: Clear screen
- `Ctrl+R`: Search history
- `Ctrl+N`: New chat
- `Ctrl+M`: Change model
- `Up/Down`: Navigate command history
- `Tab`: Auto-complete

**Implementation**:
```python
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings

bindings = KeyBindings()

@bindings.add('c-n')
def new_chat(event):
    """Start new chat on Ctrl+N."""
    event.app.exit(result='new_chat')

@bindings.add('c-m')
def change_model(event):
    """Change model on Ctrl+M."""
    event.app.exit(result='change_model')

def get_user_input() -> str:
    """Get user input with enhanced features."""
    return prompt(
        "You: ",
        history=FileHistory(str(history_file)),
        key_bindings=bindings,
        multiline=False,
    )
```

---

## Low Priority Features

### 14. Voice Input/Output
**Priority**: LOW
**Effort**: High

**Description**:
Add support for voice input and text-to-speech output.

**Usage**:
```bash
# Voice input
hi --voice

# TTS output
hi "Explain AI" --tts

# Both
hi --voice --tts
```

---

### 15. Collaborative Sessions
**Priority**: LOW
**Effort**: Very High

**Description**:
Allow multiple users to participate in the same chat session.

**Implementation**:
Would require:
- Backend server
- Session sharing mechanism
- Real-time updates
- Access control

---

### 16. Custom Model Fine-tuning Support
**Priority**: LOW
**Effort**: High

**Description**:
If Perplexity adds support for fine-tuned models, add UI for managing them.

---

### 17. Integration with System Clipboard
**Priority**: LOW
**Effort**: Low

**Description**:
Automatically copy responses to clipboard with an option.

**Usage**:
```bash
hi "Python regex example" --copy
# Response is automatically copied to clipboard
```

**Implementation**:
```python
import pyperclip

def handle_response(response: str, should_copy: bool = False):
    """Handle response with optional clipboard copy."""
    print(response)

    if should_copy:
        pyperclip.copy(response)
        print(color("\n✓ Copied to clipboard", "green"))
```

---

### 18. Emoji Reactions
**Priority**: LOW
**Effort**: Low

**Description**:
Allow users to react to AI responses with emoji ratings.

**Usage**:
```bash
AI: [Response]
Rate this response: 👍 👎 ❤️ 🤔

# Stored for improving prompts
```

---

### 19. ASCII Art Banner
**Priority**: LOW
**Effort**: Very Low

**Description**:
Add an optional ASCII art banner on startup.

```
    ____                 __         _ __
   / __ \___  _________  / /__  __ (_) /___  __
  / /_/ / _ \/ ___/ __ \/ / _ \/ |/ / / __/ / /
 / ____/  __/ /  / /_/ / /  __/>  </ / /_/ /_/
/_/    \___/_/  / .___/_/\___/_/|_/_/\__/\__, /
               /_/                       /____/

        Your CLI Companion for AI Assistance
```

---

## Feature Summary by Priority

| Priority | Count | Examples |
|----------|-------|----------|
| High     | 6     | Config files, History, Cost tracking |
| Medium   | 10    | Plugins, Templates, Batch processing |
| Low      | 6     | Voice I/O, Collaborative sessions, Clipboard |
| **Total**| **22**| |

## Implementation Roadmap

### Phase 1 (Q1) - Foundation
- Configuration file support
- History management
- Cost tracking
- Better error messages

### Phase 2 (Q2) - Enhancement
- Template system
- Streaming progress
- Output formatters
- Keyboard shortcuts

### Phase 3 (Q3) - Advanced
- Plugin system
- Batch processing
- Multi-language support
- Web search improvements

### Phase 4 (Q4) - Polish
- Voice I/O
- Collaborative sessions
- Custom integrations
- Performance optimizations
