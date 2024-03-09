#!/bin/sh
# This script is used to install the application and add it to the system path
# It is assumed that the application is already built and the binary is available
# in the current directory

set -o errexit

# check the if the terminal is bash or csh
if [[ $# -eq 0 ]] ; then
	echo 'Add the perplexity API key as an argument, you can get one form "https://www.perplexity.ai/settings/api"'
	exit 0
fi
chmod +x hi
API_KEY=$1
current_dir=$(pwd)
current_env=$(env)

  # if the terminal is bash, add the application to the path
if [ -n "$BASH" ]; then
	echo "Application added to the path"
	echo "export PATH=\$PATH:$(pwd)" >> ~/.bashrc
	echo "API key added to the path"
	echo "export PERPLEXITY_API_KEY=$API_KEY" >> ~/.bashrc
	source ~/.bashrc
elif [ -n "$ZSH_VERSION" ]; then
  # if the terminal is zsh, add the application to the path
  echo "export PATH=\$PATH:$(pwd)" >> ~/.zshrc
  echo "Application added to the path"
  echo "export PERPLEXITY_API_KEY=$API_KEY" >> ~/.zshrc
  source ~/.zshrc
else
  # if the terminal is csh, add the application to the path
  echo "setenv PATH \$PATH:$(pwd)" >> ~/.cshrc
  echo "Application added to the path"
  echo "setenv PERPLEXITY_API_KEY $API_KEY" >> ~/.cshrc
  source ~/.cshrc
fi
