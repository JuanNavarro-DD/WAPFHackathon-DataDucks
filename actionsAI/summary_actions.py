
from openai import OpenAI
import json

clientDetails = json.load(open("openai-project.json"))
client = OpenAI(organization=clientDetails["organization"], project=clientDetails["project"], api_key=clientDetails["api_key"])

def summarize_actions(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f'based on the following transcript what emergency service should we send {text} \n please only return the service name'}],
        stream=True
    )
    textResponse = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            textResponse += chunk.choices[0].delta.content
    print(textResponse)
    return textResponse