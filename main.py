import requests, os, sys, json
from dotenv import load_dotenv


load_dotenv()

if len(sys.argv) < 2:
	print("Please add your question as an argument")
	exit()

question = sys.argv[1]

context = sys.argv[2] if len(sys.argv) > 2 else "Be precise and concise"
if len(sys.argv) > 2:
	role = sys.argv[2]
url = "https://api.perplexity.ai/chat/completions"

payload = {
    "model": "sonar-small-chat",
    "messages": [
        {
            "role": "system",
            "content": context
        },
        {
            "role": "user",
            "content": question
        }
    ]
}


headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer " + os.getenv('PERPLEXITY_API_KEY')
}


response = requests.post(url, json=payload, headers=headers)


print(response.json()["choices"][0]["message"]["content"])
# parse_json = json.loads(response.text)
# print(json.dumps(parse_json, indent=4))
# print(response.json())

