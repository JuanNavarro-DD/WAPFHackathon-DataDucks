import boto3
import json
from fastapi import FastAPI

app = FastAPI()

boto3.setup_default_session(profile_name='dd-sandbox-jp')
bedrock = boto3.client('bedrock-runtime')



@app.post("/service")
def suggest_service(keywords:str) -> str:
    modelId = "mistral.mistral-7b-instruct-v0:2"

    accept = "application/json"
    contentType = "application/json"
    examplePrompt = """
        <s>[INST]
        based on the following keyworkds: 
        fire, house, emergency, burn
        Please tell me what emergency services should be sent.
        Please only return the service name.
        For example, don't say: 
        "Here are the names of the emergency services that may be needed based on your keywords:"
        I understand that I need to call emergencies but I still want to know what services should be sent.
        [/INST]fire department, ambulance</s>"""

    servicePrompt = """
        [INST]
        based on the following keyworkds:
        - [keywords]
        Please tell me what emergency services should be sent separate them with commas.
        Make sure you only return the service name and say nothing else.
        For example, don't say: 
        "Here are the names of the emergency services that may be needed based on your keywords:"
        I understand that I need to call emergencies but I still want to know what services should be sent.
        please do not return any other information or disclaimer.
        [/INST]

        """
    prompt = examplePrompt + servicePrompt

    prompt = prompt.replace("[keywords]", keywords)

    body = json.dumps({
        "prompt": prompt,
        "max_tokens": 100,
        "top_p": 0.9,
        "temperature": 1.0
    })

    response = bedrock.invoke_model(
        modelId=modelId, 
        body=body, 
        accept=accept, 
        contentType=contentType
        )
    return json.loads(response.get('body').read())["outputs"][0]["text"]