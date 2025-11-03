import requests
import os
import subprocess
import hi_constants as C
from hi_help import color

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
    print(color("Inavalid API Key. Get one and come back", "red"))
    exit(1)


def update_api_key() -> None:
    try:
        home = os.getenv("HOME")
        new_key = input("New API Key: ")
        testApiKey(new_key)
        if home is None:
            print(color("Failed to add API to shell settings", "red"))
        elif os.path.isfile(home + "/.bashrc"):
            with open(home + "/.bashrc", "a") as file:
                file.write(f"export {C.API_KEY_ENV_VAR}={new_key}\n")
            print(
                color(f"enviroment variable {C.API_KEY_ENV_VAR} added to bash", "green")
            )
        elif os.path.isfile(home + "/.cshrc"):
            with open(home + "/.cshrc", "a") as file:
                file.write(f"setenv {C.API_KEY_ENV_VAR} {new_key}\n")
            print(
                color(f"enviroment variable {C.API_KEY_ENV_VAR} added to csh", "green")
            )
        os.environ[C.API_KEY_ENV_VAR] = new_key
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
