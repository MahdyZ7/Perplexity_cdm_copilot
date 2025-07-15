# Constants
import os

API_KEY_ENV_VAR = 'PERPLEXITY_API_KEY'
API_KEY = os.getenv(API_KEY_ENV_VAR) or ""
API_URL_BASE = 'https://api.perplexity.ai'
API_URL = f'{API_URL_BASE}/chat/completions'
AVAILABLE_MODELS = ["r1-1776", "sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro", "sonar-deep-research"]
DEFAULT_CONTEXT = '''
Every input you get from me, you will:

❶. Refine the instruction to improve clarity, specificity, and effectiveness.

❷. Create a relevant perspective to adopt for interpreting the instruction.

❸. Present the refined version of the instruction using the format 'Refined: \\[$refined instruction\\]'.

❹. State the perspective you'll adopt using the format 'Perspective: \\[$chosen perspective\\]'.

❺. Execute the refined instruction from the chosen perspective and present the result using the format 'Execution: \\[$answer\\]'
'''
HEADERS = {
	"accept": "application/json",
	"content-type": "application/json",
	"authorization": f"Bearer {API_KEY}"
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