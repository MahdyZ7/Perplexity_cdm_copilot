# AI COMAND LINE HELPER

## Introduction
------------
This project provides a command-line interface (CLI) to interact with the [OpenAi](https://openai.com) [Perplexity](https://perplexityapi.com/) API. It allows users to receive responses to questions or engage in a chat session with the AI model.

You will need to sign up for an API key to use this tool.

## Features
------------

- **Question Mode**: Get a response to a specific question.
- **Chat Mode**: Engage in a continuous conversation with the AI.
- **Model Selection**: Choose from multiple AI models for different response styles.
- **System Prompt**: Set a context for the AI responses.
- **Easy Update**: Easy to update the program to the latest version.

## Installation
------------

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/MahdyZ7/Perplexity_cdm_copilot.git
   ```

2. **Install Required Packages**:
   Ensure you have Python 3.10 or higher installed. You may need to install additional packages like `requests` if they are not already available.
   ```bash
   cd Perplexity_cdm_copilot
   pip install -r requirements.txt
   ```

3. **Install the Program**:

	>You will need to sign up for an API key to use this tool. You can get an API key by signing up at [Perplexity](https://www.perplexity.ai/settings/api). ($1 can go a long way)

	To install the program, run the `install.sh` script. This will install the program and create a alias to the perplexity command in your .bashrc file.
	```bash
	bash ./install.sh
	```
	*Or* you can run the following commands to install the program manually.
	```bash
	chmod +x hi
	export $PATH=\$PATH:$PWD
	export PERPLEXITY_API_KEY=your_api_key
	```

## Usage
------------

To use the program, simply run the hi command in your terminal followed by your question. The program will then use the Perplexity API to answer your question.

- **Get Response to a Question**:
	```bash
	# basic usage
	hi "What is the capital of France?"
	```

- **Chat Mode**:
You can also chat with the program by running the ```hi chat``` command. This will start a chat session with the program.
	```bash
	hi chat
	```
- **Model Selection**:
You can specify the model and the system promt by adding optional arguments to the command.:
	```bash
	hi models
	hi "What is the capital of France?" 2 "give a single sentence answer"
	```

- **Piping Input**:
The program can read from standard input to allow for piping input
	```bash
	cat code.py | hi "explain the function fetchData() in the code"
	```

- **Updating the Program**:
You can also update the program by running the following command:
	```bash
	hi update
	```
 - **Help**:
for more information on the available options, run the following command:
	```bash
	hi help
	```

## Available Models
------------
- *sonar*
- *sonar-pro*
- *sonar-reasoning*
- *sonar-reasoning-pro*

You can list available models by running:
```bash
hi models
```

## Troubleshooting
--------------

- Ensure your API key is valid and correctly set as an environment variable.
- Check your internet connection for API requests.
- If you encounter issues updating the API key, manually add it to your shell configuration file.
	```bash
	export PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	```

