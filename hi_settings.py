import requests
import subprocess
import hi_constants as C
from hi_help import color
from pathlib import Path
import json

try:
	from rich import print
except ImportError:
	from builtins import print


def testApiKey(api_key: str) -> None:
	C.HEADERS["authorization"] = "Bearer " + api_key
	payload = {
		"model": C.AVAILABLE_MODELS[0],
		"messages": [
			{
				"role": "user",
				"content": "hi",
			}
		],
		"max_tokens": 1,
	}
	response = requests.post(C.API_URL, json=payload, headers=C.HEADERS)
	if response.status_code == 200:
		print(color("API Key is valid", "green"))
		return
	print(color("Invalid API Key. Get one and come back", "red"))
	exit(1)


def update_api_key() -> None:
	try:
		home = Path.home().as_posix()
		new_key = input("New API Key: ")
		testApiKey(new_key)
		## write api key to ~/.perplexity/apikey.json
		config_dir = Path.home() / ".perplexity"
		config_dir.mkdir(parents=True, exist_ok=True)
		config_file = config_dir / "apikey.json"
		with open(config_file, "w") as f:
			json.dump({"api_key": new_key}, f)
		print(color(f"API Key saved to {config_file}", "green"))
		C.HEADERS["authorization"] = f"Bearer {new_key}"
		print("_" * 100)
		print(">", end=" ")
	except Exception as e:
		print(
			color(
				f"Failed to accept API key: {e}. Please add {C.API_KEY_ENV_VAR} to the enviroment manually)",
				"red",
			)
		)
		exit(1)


def update() -> None:
	command_string = ["git", "pull", "-q"]
	try:
		directory: str = subprocess.run(
			["dirname", subprocess.run(["which", "hi"], capture_output=True).stdout],
			capture_output=True,
			text=True,
			timeout=5,
			check=True,
		).stdout.strip("\n")
		if directory == "." or directory is None:
			print(
				color(
					"Error: Could not find the path to 'hi' command. \
Check that you have installed hi first",
					"red",
				)
			)
			exit()
		subprocess.run(
			command_string,
			cwd=directory,
			capture_output=True,
			text=True,
			check=True,
			timeout=15,
		)
		print(color("Update run successfully", "green"))
	except subprocess.CalledProcessError as e:
		print(f"Could not update {e}")


def install():
	subprocess.run("cd $(dirname $(which hi)) ; ./install.sh")
