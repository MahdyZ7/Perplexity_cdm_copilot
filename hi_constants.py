# Constants
import os

API_KEY_ENV_VAR = 'PERPLEXITY_API_KEY'
API_KEY = os.getenv(API_KEY_ENV_VAR) or ""
API_URL = 'https://api.perplexity.ai/chat/completions'
AVAILABLE_MODELS = ["r1-1776", "sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro"]
DEFAULT_CONTEXT = "Be precise and concise"
HEADERS = {
	"accept": "application/json",
	"content-type": "application/json",
	"authorization": f"Bearer {API_KEY}"
}