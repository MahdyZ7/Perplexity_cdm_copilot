import requests, os, sys, json
from dotenv import load_dotenv
from rich import print

load_dotenv()

possible_models = ["sonar-small-chat", "sonar-medium-chat", "codellama-70b-instruct", "mistral-7b-instruct", "mixtral-8x7b-instruct"]

headers = {
	"accept": "application/json",
	"content-type": "application/json",
	"authorization": "Bearer " + os.getenv('PERPLEXITY_API_KEY')
}

url = "https://api.perplexity.ai/chat/completions"

def printAvailableModels():
	print("Available models:")
	for i in range(len(possible_models)):
		print(f"	[{i}] - {possible_models[i]}")

def pick_model(model):
	if model is None:
		return possible_models[0]
	print("Model set to " + model)
	if model.isdigit() and int(model) < len(possible_models):
		model = possible_models[int(model)]
	if model is not None and model in possible_models:
		return model
	if model != "?":
		print(f'''Invalid model name, the model will be set to {possible_models[0]}''')
		return possible_models[0]
	printAvailableModels()
	model = input(f'''Choose a model (press enter for {possible_models[0]}): ''')
	if model not in possible_models:
		print(f'''Invalid model name, the model will be set to {possible_models[0]}''')
		return possible_models[0]
	else:
		print("Model set to " + model)
		model = model
	return model

def chat_loop(question, model = possible_models[0], context= "Be precise and concise", single_use = True):
	chat_payload = {
		"model": model,
		"messages": [
			{
				"role": "system",
				"content": context
			}
		]
	}
	while (question != "exit"):
		if (single_use == False):
			question = input("You: ")
		if (question == "exit"):
			exit()
		chat_payload["messages"].append({
			"role": "user",
			"content": question
		})
		response = requests.post(url, json=chat_payload, headers=headers)
		if response.status_code != 200:
			print("Error: " + response.text)
			exit()
		chat_payload["messages"].append({
			"role": "assistant",
			"content": response.json()["choices"][0]["message"]["content"]
		})
		print("Bot: " + response.json()["choices"][0]["message"]["content"])
		if (single_use):
			return


if len(sys.argv) < 2 or sys.argv[1] == "help":
	print("welcome to the perplexity command line ai!")
	print(f'''
	This is a simple command line interface to interact with the perplexity api in one of two ways: 
	  - get a response to a question
	  - chat with the bot.
	To get a response to a question, use the following syntax:
	  - CMD "Question" "System prompt (Optinal)" "Model (Optinal)"
	  E.g. CMD "What is the capital of Nigeria?" "Be precise and concise" "sonar-small-chat"
	To chat with the bot, use the following syntax:
	  - CMD "chat" "System prompt (Optinal)" "Model (Optinal)"
	  E.g. CMD "chat" "Be precise and concise" "sonar-small-chat"
	To see the available models, use the following syntax:
	  - CMD "models"
	  The available models are: (you can use the number to select the model)
	''')
	for i in range(len(possible_models)):
		print(f"	[{i}] - {possible_models[i]}")
	print(f'''
	To exit the chat, type "exit" at any time.
	''')

	exit()

# params
question = sys.argv[1]
context = sys.argv[2] if len(sys.argv) > 2 else "Be precise and concise, give an example if possible."
model = pick_model(sys.argv[3] if len(sys.argv) > 3 else None)

if question == "models":
	print("Available models:" + str(possible_models))
	exit()


single_use = False if question == "chat" else True
chat_loop(question, model, context, single_use)


