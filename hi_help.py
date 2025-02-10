import hi_constants as CONST

def availableModels() -> str:
	models = "\t Available models:\n"
	for i in range(len(CONST.AVAILABLE_MODELS)):
		models += f"		[{i}] - {CONST.AVAILABLE_MODELS[i]}\n"
	return models

def printAvailableModels():
	print(availableModels())

def pick_model(model: str) -> str:
	if not model:
		return CONST.AVAILABLE_MODELS[0]
	if model in CONST.AVAILABLE_MODELS:
		return model
	model = model.lower()
	match model:
		case "s" | "so" | "small" | "0":
			return CONST.AVAILABLE_MODELS[0]
		case "l" | "lo" | "long" | "1" | "pro":
			return CONST.AVAILABLE_MODELS[1]
		case "r" | "re" | "res" | "reasoning" | "2":
			return CONST.AVAILABLE_MODELS[2]
		case "rp" | "r-pro" | "rpro" | "reasoning-pro" | "3":
			return CONST.AVAILABLE_MODELS[3]
		case "?" | "help" | "h" | "models":
			printAvailableModels()
			model = input(f'''Choose a model (press enter for {CONST.AVAILABLE_MODELS[0]}): ''')
			return pick_model(model)
		case _:
			print(f'''Invalid model name, the model will be set to {CONST.AVAILABLE_MODELS[0]}''')
			return CONST.AVAILABLE_MODELS[0]
		
def description() -> str:
	return (f'''welcome to the perplexity command line ai
This is a simple command line interface to interact with the perplexity AI: 
	- Get a response to a question
		E.g. hi "What is the capital of Nigeria?" 0 {CONST.DEFAULT_CONTEXT} 
		Use the following syntax:
		- hi "Question" "Model (Optinal)" "System prompt (Optinal)"
	- Chat with the bot:
		E.g. hi "chat" 1 {CONST.DEFAULT_CONTEXT} 
		- CMD "chat" "Model (Optinal)" "System prompt (Optinal)"
		To exit the chat, type "exit" at any time.
	To see the available models, use the following syntax:
		- hi models
{availableModels()}
		''')
