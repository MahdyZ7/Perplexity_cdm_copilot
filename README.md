# AI Command Line Helper

## Introduction

This project provides a command-line interface (CLI) to interact with the [Perplexity API](https://perplexityapi.com/). It allows users to receive responses to questions or engage in a chat session with AI models.

You will need to sign up for an API key to use this tool (get one at [Perplexity Settings](https://www.perplexity.ai/settings/api) - $1 can go a long way).

## Features

- **Question Mode**: Get instant responses to specific questions
- **Chat Mode**: Engage in continuous conversations with AI
- **Model Selection**: Choose from multiple Perplexity models (sonar, sonar-pro, sonar-reasoning, etc.)
- **System Prompts**: Customize the AI's behavior with custom contexts
- **Search Filtering**: Include/exclude specific domains and set recency filters
- **Pipe Input Support**: Process code or text files directly through stdin
- **Easy Updates**: Built-in self-update functionality via git

## Installation

### Prerequisites
- Python 3.10 or 3.11 (3.12+ not currently supported)
- [uv](https://github.com/astral-sh/uv) package manager (will be installed automatically if missing)
- A Perplexity API key from [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)

### Quick Install

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/MahdyZ7/Perplexity_cdm_copilot.git
   cd Perplexity_cdm_copilot
   ```

2. **Run the Install Script**:
   ```bash
   bash ./install.sh YOUR_API_KEY
   ```

   This will:
   - Install `uv` if not present
   - Make the `hi` command executable
   - Add the repository to your PATH
   - Save your API key to your shell config (~/.bashrc, ~/.zshrc, or ~/.cshrc)

3. **Reload Your Shell**:
   ```bash
   source ~/.bashrc  # or ~/.zshrc if using zsh
   ```

### Manual Installation

If you prefer manual setup:

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Make executable
chmod +x hi

# Add to PATH (choose your shell config file)
echo "export PATH=\$PATH:$(pwd)" >> ~/.bashrc
echo "export PERPLEXITY_API_KEY=your_api_key_here" >> ~/.bashrc

# Reload shell
source ~/.bashrc
```

## Usage

### Basic Question Mode

Ask a single question and get an instant response:

```bash
hi "What is the capital of France?"
```

### Chat Mode

Start an interactive conversation:

```bash
hi chat
```

Within chat mode, you can use special commands:
- Type `new chat` to start a fresh conversation
- Type `change model` to switch AI models mid-conversation
- Type `exit` to quit

### Model Selection

List available models:
```bash
hi models
```

Available models:
- **sonar** (0, s, small) - Fast, general-purpose responses
- **sonar-pro** (1, l, long, pro) - More detailed responses
- **sonar-reasoning** (2, r, reasoning) - Step-by-step logical thinking
- **sonar-reasoning-pro** (3, rp, rpro) - Advanced reasoning capabilities
- **sonar-deep-research** (4, d, deep) - In-depth research and analysis

Specify a model by number or alias:
```bash
hi "Explain quantum computing" 2
hi "Explain quantum computing" reasoning
```

### Custom System Prompts

Customize the AI's behavior with a system prompt:

```bash
hi "What is the capital of France?" 0 "give a single sentence answer"
hi "Explain recursion" pro "you are a patient teacher explaining to a beginner"
```

### Advanced Search Options

Filter search results by domain:
```bash
# Include only specific domains
hi "latest Python news" -i python.org github.com

# Exclude specific domains
hi "React tutorials" -e reddit.com stackoverflow.com
```

Set time-based search filters:
```bash
# Recent results only
hi "AI developments" -T day    # last day
hi "tech news" -T week          # last week
hi "market trends" -T month     # last month
```

Get related questions:
```bash
hi "machine learning basics" -R
```

### Piping Input

Process files or command output directly:

```bash
# Analyze code
cat script.py | hi "explain what this code does"

# Review git diff
git diff | hi "summarize these changes"

# Process documentation
cat README.md | hi "create a quick start guide from this"
```

### Updating

Keep the tool up to date:
```bash
hi update
```

### Getting Help

```bash
hi help
hi ?
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_hi.py

# Run specific test function
uv run pytest tests/test_hi.py::test_pick_model -v
```

### Project Structure

```
.
├── hi                  # Main executable (Python script with uv shebang)
├── hi_constants.py     # Configuration, API endpoints, models
├── hi_help.py         # Help text and model selection logic
├── hi_settings.py     # API key management and update functionality
├── install.sh         # Installation script
├── tests/
│   └── test_hi.py    # Pytest test suite
└── pyproject.toml    # Project dependencies and metadata
```

## Troubleshooting

### API Key Issues

- **Error: "Please set the PERPLEXITY_API_KEY environment variable"**
  ```bash
  export PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  source ~/.bashrc  # or your shell config file
  ```

- **Invalid API Key**
  - Verify your key at [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
  - Check for extra spaces or quotes in the key

### Installation Issues

- **"command not found: hi"**
  - Make sure you've sourced your shell config: `source ~/.bashrc`
  - Verify the repository is in your PATH: `echo $PATH`
  - Check the script is executable: `ls -la hi`

- **Python version error**
  - This tool requires Python 3.10 or 3.11
  - Check your version: `python3 --version`

### Runtime Issues

- **Request timeout**
  - Check your internet connection
  - Try a faster model (sonar instead of sonar-pro)

- **Rate limit exceeded**
  - Wait a moment before retrying
  - Check your API usage at Perplexity dashboard

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Known Issues

See `FIXES_NEEDED.md` and `IMPROVEMENTS.md` for documented bugs and planned improvements.

## License

This project is open source. Please check the repository for license details.

