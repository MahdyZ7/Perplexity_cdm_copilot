# Architecture and Structure Recommendations

This document outlines architectural improvements and structural reorganization suggestions to make the codebase more maintainable, scalable, and professional.

## Current Architecture Issues

### Problems with Current Structure

1. **Flat File Structure**: All Python modules in root directory
2. **Single Monolithic Script**: `hi` script contains too many responsibilities
3. **No Clear Separation of Concerns**: Business logic mixed with CLI handling
4. **Global State**: Constants file has side effects (loads API key on import)
5. **No Package Structure**: Not installable as a proper Python package
6. **Testing Challenges**: Hard to test due to tight coupling

---

## Recommended Architecture

### 1. Package-Based Structure
**Priority**: HIGH
**Effort**: Medium

Transform from a script-based tool to a proper Python package.

**Proposed Structure**:
```
perplexity_cli/
├── pyproject.toml
├── README.md
├── CLAUDE.md
├── LICENSE
├── .gitignore
├── Docs/
│   ├── Issues.md
│   ├── Features.md
│   └── Architecture.md
│
├── src/
│   └── perplexity_cli/
│       ├── __init__.py
│       ├── __main__.py              # Entry point for 'python -m perplexity_cli'
│       │
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py              # CLI entry point and argument parsing
│       │   ├── commands.py          # Command implementations
│       │   └── prompts.py           # User input handling
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── client.py            # API client
│       │   ├── models.py            # Data models (Pydantic)
│       │   ├── streaming.py         # Streaming logic
│       │   └── validators.py        # Input validation
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py          # Configuration management
│       │   ├── constants.py         # Constants only (no side effects)
│       │   └── loader.py            # Config file loading
│       │
│       ├── history/
│       │   ├── __init__.py
│       │   ├── manager.py           # History management
│       │   └── storage.py           # Storage backend
│       │
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── colors.py            # Terminal colors
│       │   ├── formatters.py        # Output formatting
│       │   └── errors.py            # Custom exceptions
│       │
│       └── plugins/                 # Future plugin system
│           ├── __init__.py
│           └── base.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_client.py
│   │   ├── test_validators.py
│   │   ├── test_config.py
│   │   └── test_formatters.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_integration.py
│   │   └── test_cli_integration.py
│   │
│   └── security/
│       ├── __init__.py
│       └── test_input_validation.py
│
└── scripts/
    ├── install.sh                   # Installation script
    └── benchmark.py                 # Performance benchmarks
```

**Benefits**:
- Clear separation of concerns
- Easy to test individual components
- Professional package structure
- Installable via pip
- Better IDE support

---

### 2. Dependency Injection Pattern
**Priority**: HIGH
**Effort**: Medium

Remove global state and use dependency injection for better testability.

**Current Problem**:
```python
# hi_constants.py
API_KEY = os.getenv("PERPLEXITY_API_KEY")  # Side effect on import
HEADERS = {"authorization": f"Bearer {API_KEY}"}  # Depends on side effect
```

**Recommended Approach**:
```python
# src/perplexity_cli/core/client.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class APIConfig:
    """API configuration."""
    api_key: str
    base_url: str = "https://api.perplexity.ai"
    timeout: int = 300

    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Create config from environment."""
        api_key = os.getenv("PERPLEXITY_API_KEY", "")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        return cls(api_key=api_key)

    @classmethod
    def from_file(cls, config_path: Path) -> 'APIConfig':
        """Load config from file."""
        # Load from TOML/JSON
        pass

class PerplexityClient:
    """Client for Perplexity API."""

    def __init__(self, config: APIConfig):
        self.config = config
        self._session: Optional[requests.Session] = None

    @property
    def session(self) -> requests.Session:
        """Lazy-loaded session with proper headers."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {self.config.api_key}"
            })
        return self._session

    def send_request(
        self,
        messages: List[Dict[str, str]],
        model: str = "sonar",
        **kwargs
    ) -> str:
        """Send API request."""
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        response = self.session.post(
            f"{self.config.base_url}/chat/completions",
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

# Usage:
config = APIConfig.from_env()
client = PerplexityClient(config)
response = client.send_request(messages=[...])
```

**Benefits**:
- No global state
- Easy to test with mock configs
- Clear dependencies
- Configuration can be changed at runtime

---

### 3. Domain Models with Pydantic
**Priority**: HIGH
**Effort**: Low

Use Pydantic for data validation and type safety.

**Implementation**:
```python
# src/perplexity_cli/core/models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime

class Message(BaseModel):
    """Chat message model."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        if len(v) > 10000:
            raise ValueError("Content too long (max 10000 characters)")
        return v.strip()

class ChatRequest(BaseModel):
    """API request model."""
    model: str = "sonar"
    messages: List[Message]
    search_domain_filter: Optional[List[str]] = None
    search_recency_filter: Optional[Literal["month", "week", "day", "hour"]] = None
    return_related_questions: bool = False

    @validator("model")
    def validate_model(cls, v):
        valid_models = ["sonar", "sonar-pro", "sonar-reasoning",
                       "sonar-reasoning-pro", "sonar-deep-research"]
        if v not in valid_models:
            raise ValueError(f"Invalid model: {v}")
        return v

class SearchResult(BaseModel):
    """Search result model."""
    title: str
    url: str
    date: Optional[str] = None
    relevance: Optional[float] = None

class ChatResponse(BaseModel):
    """API response model."""
    content: str
    model: str
    search_results: Optional[List[SearchResult]] = None
    related_questions: Optional[List[str]] = None

# Usage:
try:
    request = ChatRequest(
        model="sonar",
        messages=[Message(role="user", content="Hello")]
    )
    # Automatically validated
except ValidationError as e:
    print(f"Invalid request: {e}")
```

**Benefits**:
- Automatic validation
- Type safety
- Self-documenting code
- Easy serialization/deserialization

---

### 4. Command Pattern for CLI
**Priority**: MEDIUM
**Effort**: Medium

Use command pattern to organize CLI commands.

**Implementation**:
```python
# src/perplexity_cli/cli/commands.py
from abc import ABC, abstractmethod
from typing import Dict, Type

class Command(ABC):
    """Base command interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name."""
        pass

    @property
    @abstractmethod
    def help(self) -> str:
        """Help text."""
        pass

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """Execute command. Returns exit code."""
        pass

class AskCommand(Command):
    """Single question command."""

    def __init__(self, client: PerplexityClient):
        self.client = client

    @property
    def name(self) -> str:
        return "ask"

    @property
    def help(self) -> str:
        return "Ask a single question"

    def execute(self, args: argparse.Namespace) -> int:
        try:
            response = self.client.send_request(
                messages=[Message(role="user", content=args.question)]
            )
            print(response)
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

class ChatCommand(Command):
    """Interactive chat command."""

    def __init__(self, client: PerplexityClient, history: HistoryManager):
        self.client = client
        self.history = history

    @property
    def name(self) -> str:
        return "chat"

    @property
    def help(self) -> str:
        return "Start interactive chat session"

    def execute(self, args: argparse.Namespace) -> int:
        session_id = self.history.new_session()
        # Chat loop implementation
        return 0

class CommandRegistry:
    """Registry of available commands."""

    def __init__(self):
        self._commands: Dict[str, Command] = {}

    def register(self, command: Command):
        """Register a command."""
        self._commands[command.name] = command

    def get(self, name: str) -> Optional[Command]:
        """Get command by name."""
        return self._commands.get(name)

    def list_commands(self) -> List[Command]:
        """List all commands."""
        return list(self._commands.values())

# Usage in main.py:
def main():
    config = APIConfig.from_env()
    client = PerplexityClient(config)
    history = HistoryManager()

    registry = CommandRegistry()
    registry.register(AskCommand(client))
    registry.register(ChatCommand(client, history))
    registry.register(HistoryCommand(history))
    registry.register(ModelsCommand())

    args = parse_args()

    command = registry.get(args.command)
    if command:
        return command.execute(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1
```

**Benefits**:
- Easy to add new commands
- Each command is independently testable
- Clear separation of concerns
- Plugin-friendly architecture

---

### 5. Strategy Pattern for Output Formatting
**Priority**: MEDIUM
**Effort**: Low

Use strategy pattern for different output formats.

**Implementation**:
```python
# src/perplexity_cli/utils/formatters.py
from abc import ABC, abstractmethod

class OutputFormatter(ABC):
    """Base formatter interface."""

    @abstractmethod
    def format(self, response: ChatResponse) -> str:
        """Format the response."""
        pass

class PlainTextFormatter(OutputFormatter):
    """Plain text output."""

    def format(self, response: ChatResponse) -> str:
        output = [response.content]

        if response.search_results:
            output.append("\n--- Search Results ---")
            for i, result in enumerate(response.search_results, 1):
                output.append(f"[{i}] {result.title} - {result.url}")

        return "\n".join(output)

class MarkdownFormatter(OutputFormatter):
    """Markdown output."""

    def format(self, response: ChatResponse) -> str:
        output = [f"# Response\n\n{response.content}"]

        if response.search_results:
            output.append("\n## Sources\n")
            for result in response.search_results:
                output.append(f"- [{result.title}]({result.url})")

        return "\n".join(output)

class JSONFormatter(OutputFormatter):
    """JSON output."""

    def format(self, response: ChatResponse) -> str:
        return response.json(indent=2)

class FormatterFactory:
    """Factory for creating formatters."""

    _formatters = {
        "plain": PlainTextFormatter,
        "markdown": MarkdownFormatter,
        "json": JSONFormatter,
    }

    @classmethod
    def create(cls, format_type: str) -> OutputFormatter:
        """Create formatter by type."""
        formatter_class = cls._formatters.get(format_type)
        if not formatter_class:
            raise ValueError(f"Unknown format: {format_type}")
        return formatter_class()

# Usage:
formatter = FormatterFactory.create(args.format)
output = formatter.format(response)
print(output)
```

**Benefits**:
- Easy to add new formats
- Each formatter is independently testable
- Clean separation of concerns
- User can choose output format

---

### 6. Repository Pattern for History Storage
**Priority**: MEDIUM
**Effort**: Medium

Abstract storage backend for flexibility.

**Implementation**:
```python
# src/perplexity_cli/history/storage.py
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
import json

class HistoryStorage(ABC):
    """Abstract storage interface."""

    @abstractmethod
    def save_session(self, session_id: str, messages: List[Message]):
        """Save session."""
        pass

    @abstractmethod
    def load_session(self, session_id: str) -> Optional[List[Message]]:
        """Load session."""
        pass

    @abstractmethod
    def list_sessions(self) -> List[str]:
        """List all sessions."""
        pass

    @abstractmethod
    def delete_session(self, session_id: str):
        """Delete session."""
        pass

class JSONFileStorage(HistoryStorage):
    """JSON file-based storage."""

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_id: str, messages: List[Message]):
        file_path = self.storage_dir / f"{session_id}.json"
        data = [msg.dict() for msg in messages]
        file_path.write_text(json.dumps(data, indent=2, default=str))

    def load_session(self, session_id: str) -> Optional[List[Message]]:
        file_path = self.storage_dir / f"{session_id}.json"
        if not file_path.exists():
            return None
        data = json.loads(file_path.read_text())
        return [Message(**msg) for msg in data]

    def list_sessions(self) -> List[str]:
        return [f.stem for f in self.storage_dir.glob("*.json")]

    def delete_session(self, session_id: str):
        file_path = self.storage_dir / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()

class SQLiteStorage(HistoryStorage):
    """SQLite-based storage for better querying."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        # Create tables
        pass

    # Implement interface methods...

# src/perplexity_cli/history/manager.py
class HistoryManager:
    """History management with pluggable storage."""

    def __init__(self, storage: HistoryStorage):
        self.storage = storage
        self.current_session: Optional[str] = None
        self.current_messages: List[Message] = []

    def new_session(self) -> str:
        """Start new session."""
        self.current_session = str(uuid.uuid4())
        self.current_messages = []
        return self.current_session

    def add_message(self, message: Message):
        """Add message to current session."""
        self.current_messages.append(message)
        if self.current_session:
            self.storage.save_session(self.current_session, self.current_messages)

    def resume_session(self, session_id: str) -> bool:
        """Resume previous session."""
        messages = self.storage.load_session(session_id)
        if messages:
            self.current_session = session_id
            self.current_messages = messages
            return True
        return False

# Usage:
storage = JSONFileStorage(Path.home() / ".local" / "share" / "perplexity" / "history")
history = HistoryManager(storage)
```

**Benefits**:
- Easy to swap storage backends
- Testable with in-memory storage
- Can add SQLite, Redis, etc. without changing code
- Clear interface

---

### 7. Error Handling Hierarchy
**Priority**: HIGH
**Effort**: Low

Create custom exception hierarchy for better error handling.

**Implementation**:
```python
# src/perplexity_cli/utils/errors.py
class PerplexityError(Exception):
    """Base exception for all perplexity errors."""

    def __init__(self, message: str, exit_code: int = 1):
        self.message = message
        self.exit_code = exit_code
        super().__init__(message)

class ConfigurationError(PerplexityError):
    """Configuration-related errors."""

    def __init__(self, message: str):
        super().__init__(message, exit_code=2)

class APIError(PerplexityError):
    """API-related errors."""
    pass

class AuthenticationError(APIError):
    """Authentication failures."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message, exit_code=3)

class RateLimitError(APIError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, exit_code=4)

class NetworkError(APIError):
    """Network connectivity issues."""

    def __init__(self, message: str = "Network error"):
        super().__init__(message, exit_code=5)

class ValidationError(PerplexityError):
    """Input validation errors."""

    def __init__(self, message: str):
        super().__init__(message, exit_code=6)

# Error handler
class ErrorHandler:
    """Centralized error handling."""

    @staticmethod
    def handle(error: Exception) -> int:
        """Handle error and return exit code."""
        if isinstance(error, AuthenticationError):
            print(color("⚠ Authentication Error", "red"))
            print(f"{error.message}")
            print("\nSuggestions:")
            print("  • Verify your key at https://www.perplexity.ai/settings/api")
            print("  • Check PERPLEXITY_API_KEY environment variable")
            return error.exit_code

        elif isinstance(error, RateLimitError):
            print(color("⚠ Rate Limit Error", "red"))
            print(f"{error.message}")
            print("\nSuggestions:")
            print("  • Wait a moment before retrying")
            print("  • Check your API usage dashboard")
            return error.exit_code

        # ... handle other error types

        else:
            print(color(f"⚠ Unexpected Error: {error}", "red"))
            return 1

# Usage in main:
def main():
    try:
        # Application logic
        pass
    except PerplexityError as e:
        return ErrorHandler.handle(e)
    except Exception as e:
        logger.exception("Unexpected error")
        return ErrorHandler.handle(e)
```

**Benefits**:
- Clear error types
- Consistent error handling
- Specific exit codes for scripting
- User-friendly error messages

---

### 8. Configuration Management System
**Priority**: HIGH
**Effort**: Medium

Implement layered configuration system.

**Configuration Priority** (highest to lowest):
1. Command-line arguments
2. Environment variables
3. User config file (`~/.config/perplexity/config.toml`)
4. System config file (`/etc/perplexity/config.toml`)
5. Default values

**Implementation**:
```python
# src/perplexity_cli/config/loader.py
from pathlib import Path
from typing import Optional, Any
import tomli
import os

class ConfigLoader:
    """Layered configuration loader."""

    DEFAULT_CONFIG = {
        "api": {
            "base_url": "https://api.perplexity.ai",
            "timeout": 300,
            "default_model": "sonar",
        },
        "display": {
            "color": True,
            "format": "plain",
        },
        "history": {
            "enabled": True,
            "max_sessions": 100,
        }
    }

    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_layers()

    def _load_layers(self):
        """Load configuration from all layers."""
        # 1. System config
        system_config = Path("/etc/perplexity/config.toml")
        if system_config.exists():
            self._merge_config(self._load_toml(system_config))

        # 2. User config
        user_config = Path.home() / ".config" / "perplexity" / "config.toml"
        if user_config.exists():
            self._merge_config(self._load_toml(user_config))

        # 3. Environment variables
        self._load_env_vars()

    def _load_toml(self, path: Path) -> dict:
        """Load TOML file."""
        with open(path, "rb") as f:
            return tomli.load(f)

    def _merge_config(self, new_config: dict):
        """Merge new config into existing."""
        # Deep merge dictionaries
        def deep_merge(base: dict, update: dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value

        deep_merge(self.config, new_config)

    def _load_env_vars(self):
        """Load configuration from environment variables."""
        # PERPLEXITY_API_KEY
        if api_key := os.getenv("PERPLEXITY_API_KEY"):
            self.config.setdefault("api", {})["key"] = api_key

        # PERPLEXITY_MODEL
        if model := os.getenv("PERPLEXITY_MODEL"):
            self.config["api"]["default_model"] = model

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def override(self, key: str, value: Any):
        """Override configuration value (from CLI args)."""
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            config = config.setdefault(k, {})

        config[keys[-1]] = value

# Usage:
config = ConfigLoader()
api_key = config.get("api.key")
timeout = config.get("api.timeout", 300)

# Override from CLI
config.override("api.default_model", args.model)
```

---

### 9. Logging System
**Priority**: MEDIUM
**Effort**: Low

Implement proper logging with levels and rotation.

**Implementation**:
```python
# src/perplexity_cli/utils/logging.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    log_to_console: bool = False
):
    """Setup logging configuration."""

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Root logger
    logger = logging.getLogger("perplexity_cli")
    logger.setLevel(getattr(logging, log_level.upper()))

    # File handler with rotation
    if log_file is None:
        log_dir = Path.home() / ".local" / "share" / "perplexity" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "perplexity.log"

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (only for debug mode)
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)
        logger.addHandler(console_handler)

    return logger

# Usage:
logger = setup_logging(
    log_level=config.get("logging.level", "INFO"),
    log_to_console=args.debug
)

logger.info("Application started")
logger.debug(f"Using model: {model}")
logger.error(f"API request failed: {e}")
```

---

### 10. Testing Architecture
**Priority**: HIGH
**Effort**: Medium

Implement comprehensive testing strategy.

**Structure**:
```python
# tests/conftest.py
import pytest
from pathlib import Path
from perplexity_cli.core.client import APIConfig, PerplexityClient
from perplexity_cli.history.storage import HistoryStorage
from perplexity_cli.core.models import Message

@pytest.fixture
def mock_config():
    """Mock API configuration."""
    return APIConfig(
        api_key="test-key",
        base_url="https://test.api.com",
        timeout=10
    )

@pytest.fixture
def mock_client(mock_config):
    """Mock client for testing."""
    return PerplexityClient(mock_config)

@pytest.fixture
def temp_storage(tmp_path):
    """Temporary storage for testing."""
    from perplexity_cli.history.storage import JSONFileStorage
    return JSONFileStorage(tmp_path / "history")

@pytest.fixture
def sample_messages():
    """Sample messages for testing."""
    return [
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there!"),
    ]

# tests/unit/test_client.py
def test_client_initialization(mock_config):
    """Test client initialization."""
    client = PerplexityClient(mock_config)
    assert client.config.api_key == "test-key"

def test_send_request_success(mock_client, requests_mock):
    """Test successful API request."""
    requests_mock.post(
        "https://test.api.com/chat/completions",
        json={"choices": [{"message": {"content": "Test response"}}]}
    )

    response = mock_client.send_request(
        messages=[{"role": "user", "content": "test"}]
    )

    assert response == "Test response"

# tests/integration/test_api_integration.py
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("PERPLEXITY_API_KEY"), reason="No API key")
def test_real_api_call():
    """Test actual API integration."""
    config = APIConfig.from_env()
    client = PerplexityClient(config)

    response = client.send_request(
        messages=[Message(role="user", content="What is 2+2?")]
    )

    assert response
    assert len(response) > 0

# tests/security/test_input_validation.py
def test_message_validation():
    """Test message content validation."""
    with pytest.raises(ValidationError):
        Message(role="user", content="")

    with pytest.raises(ValidationError):
        Message(role="user", content="a" * 10001)

def test_null_byte_removal():
    """Test null byte handling."""
    content = "test\x00malicious"
    # Should be sanitized
```

---

## Migration Strategy

### Phase 1: Preparation (Week 1)
1. Create new package structure
2. Set up pyproject.toml with dependencies
3. Create base classes and interfaces
4. Set up testing infrastructure

### Phase 2: Core Migration (Week 2-3)
1. Move constants to proper config module
2. Implement APIConfig and PerplexityClient
3. Create Pydantic models
4. Implement validators
5. Add comprehensive tests

### Phase 3: CLI Restructuring (Week 4)
1. Implement command pattern
2. Move CLI logic to separate modules
3. Add command registry
4. Update entry points

### Phase 4: Additional Features (Week 5-6)
1. Implement history manager with storage abstraction
2. Add formatters
3. Implement error handling hierarchy
4. Add logging

### Phase 5: Testing & Documentation (Week 7)
1. Achieve >80% test coverage
2. Write integration tests
3. Update documentation
4. Create migration guide for users

### Phase 6: Deployment (Week 8)
1. Package for PyPI
2. Update installation instructions
3. Deprecate old structure
4. Provide migration path

---

## Benefits of New Architecture

1. **Maintainability**: Clear structure, easy to find and modify code
2. **Testability**: Dependency injection, mockable components
3. **Scalability**: Easy to add new features without breaking existing code
4. **Professional**: Industry-standard patterns and practices
5. **Reusability**: Components can be used independently
6. **Type Safety**: Pydantic models and comprehensive type hints
7. **Flexibility**: Plugin system, swappable backends
8. **Reliability**: Comprehensive testing, proper error handling

---

## Key Principles to Follow

1. **SOLID Principles**
   - Single Responsibility: Each class has one job
   - Open/Closed: Open for extension, closed for modification
   - Liskov Substitution: Subtypes must be substitutable
   - Interface Segregation: Many specific interfaces better than one general
   - Dependency Inversion: Depend on abstractions, not concretions

2. **DRY (Don't Repeat Yourself)**
   - Remove duplicate code
   - Create reusable components
   - Use inheritance and composition appropriately

3. **KISS (Keep It Simple, Stupid)**
   - Simple solutions over complex ones
   - Clear naming
   - Short, focused functions

4. **YAGNI (You Aren't Gonna Need It)**
   - Don't add features until needed
   - Focus on current requirements
   - Refactor when necessary

5. **Testing Best Practices**
   - Write tests first (TDD when appropriate)
   - Aim for high coverage
   - Test behavior, not implementation
   - Use fixtures and mocks appropriately
