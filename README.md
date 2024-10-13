# PERPLIXITY COMAND LINE chat

This program is a command line tool that uses the [Perplexity](https://perplexityapi.com/) API to answer questions and chat in the terminal.
You will need to sign up for an API key to use this tool.

## Installation
To install the program, run the install.sh script. This will install the program and create a symlink to the perplexity command in your /usr/local/bin directory.
```bash
bash ./install.sh
```
Or you can run the following commands to install the program manually.
```bash
chmod +x hi
export $PATH=\$PATH:$PWD
export PERPLIXITY_API_KEY=your_api_key
```

## Usage

To use the program, simply run the hi command in your terminal followed by your question. The program will then use the Perplexity API to answer your question.

```bash
# basic usage
hi "What is the capital of France?"
```

You can also chat with the program by running the ```hi chat``` command. This will start a chat session with the program.
```bash
hi chat
```

You can specify the model and the system promt by adding optional arguments to the command.:
```bash
hi models
hi "What is the capital of France?" 2 "give a single sentence answer"
```

The program can read from standard input to allow for piping input
```bash
cat code.py | hi "explain the function fetchData() in the code"
```

for more information on the available options, run the following command:
```bash
hi help

```

