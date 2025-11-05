#!/bin/sh
# This script is used to install the application and add it to the system path
# It is assumed that the application is already built and the binary is available
# in the current directory

set -o errexit

# check the if the terminal is bash or csh
if [ $# -eq 0 ] ; then
	echo 'Add the perplexity API key as an argument, you can get one form "https://www.perplexity.ai/settings/api"'
	exit 0
fi
chmod +x hi
API_KEY=$1
current_dir=$(pwd)
current_env=$(env)

# install UV
if ! command -v uv >/dev/null 2>&1; then
  echo "UV is not installed. Installing UV..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# create the .perplexity directory in the home directory
mkdir -p ~/.perplexity
chmod 700 ~/.perplexity
# create the apikey.json file in the .perplexity directory
echo "{\"api_key\": \"$API_KEY\"}" > ~/.perplexity/apikey.json
chmod 600 ~/.perplexity/apikey.json
