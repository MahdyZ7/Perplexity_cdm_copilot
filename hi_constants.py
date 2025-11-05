# Constants
import os
from pathlib import Path
import json

def _load_api_key() -> str:
	# Deprecated method of loading API key
	api_key = os.getenv("PERPLEXITY_API_KEY")
	if api_key:
		return api_key
	# Load from config file
	config_file = Path.home() / ".perplexity" / "apikey.json"
	if config_file.exists():
		with open(config_file, "r") as f:
			config = json.load(f)
			key = config.get("api_key", "")
			if key:
				os.environ["PERPLEXITY_API_KEY"] = key
				return key
	return ""

API_KEY_ENV_VAR = "PERPLEXITY_API_KEY"
API_KEY = _load_api_key()
API_URL_BASE = "https://api.perplexity.ai"
API_URL = f"{API_URL_BASE}/chat/completions"
AVAILABLE_MODELS = [
	"sonar",
	"sonar-pro",
	"sonar-reasoning",
	"sonar-reasoning-pro",
	"sonar-deep-research",
]
DEFAULT_MODEL = AVAILABLE_MODELS[0]
DEFAULT_CONTEXT = """You are an expert research assistant specializing in technology and science. 
Always provide well-sourced, accurate information and cite your sources. 
Format your responses with clear headings and bullet points when appropriate."""
# DEFAULT_CONTEXT = '''
# Every input you get from me, you will:

# ❶. Refine the instruction to improve clarity, specificity, and effectiveness.

# ❷. Create a relevant perspective to adopt for interpreting the instruction.

# ❸. Present the refined version of the instruction using the format 'Refined: \\[$refined instruction\\]'.

# ❹. State the perspective you'll adopt using the format 'Perspective: \\[$chosen perspective\\]'.

# ❺. Execute the refined instruction from the chosen perspective and present the result using the format 'Execution: \\[$answer\\]'
# '''
HEADERS = {
	"accept": "application/json",
	"content-type": "application/json",
	"authorization": f"Bearer {API_KEY}",
}
TIMEOUT = 7200
COLORS = {
	"red": "\033[31m",
	"green": "\033[32m",
	"yellow": "\033[33m",
	"blue": "\033[34m",
	"magenta": "\033[35m",
	"cyan": "\033[36m",
	"reset": "\033[0m",
}

# OpenAI Constants
# API_URL_BASE = "https://api.openai.com/v1"
# API_URL = f'{API_URL_BASE}/chat/completions'
# AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4o", "o3-mini", "o1"]
