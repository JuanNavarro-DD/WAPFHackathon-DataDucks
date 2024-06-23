# from fastapi import FastAPI
from typing import List, Dict
#import json
#from keybert.llm import TextGeneration
from keybert.llm import LangChain
from keybert import KeyLLM

# from ctransformers import AutoModelForCausalLM
# from transformers import pipeline, AutoTokenizer

# from huggingface_hub import login

from langchain.chains.question_answering import load_qa_chain
#from langchain.llms import Bedrock
from langchain_aws import BedrockLLM as Bedrock


import boto3
import json
from fastapi import FastAPI

app = FastAPI()

boto3.setup_default_session(profile_name='dd-sandbox-jp')
bedrock = boto3.client('bedrock-runtime')



# HFToken = json.load(open("huggingFaceToken.json"))["token"]

# login(token=HFToken) 
app = FastAPI()

#Setup the llm
# model = AutoModelForCausalLM.from_pretrained("../../../models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
#                                              model_type="mistral",
#                                              gpu_layers=0,
#                                              hf=True) 

# #Tokeniser from hugging face model
# tokenizer = AutoTokenizer.from_pretrained("mistralai/mistral-7b-instruct-v0.1")

#Pipeline
# generator = pipeline(model=model,
#                      tokenizer=tokenizer,
#                      task='text-generation',
#                      max_new_tokens=500,
#                      repetition_penalty=1.1)


example_prompt = """
<s>[INST]
I have the following document: 
- The website mentions that it only takes a couple of days to deliver but I still have not received mine.
Please give me 5 keywords that are present in this document and separate them with commas.
Make sure you only return the keywords and say nothing else.
Do not provide additional context
For example, don't say: 
"Here are the keywords present in the document"
[/INST] potato, badger, kestral, concept, class</s>"""

kw_prompt = """
[INST]
I have the following document:
- [DOCUMENT]
Please give me 5 keywords that are present in this document and separate them with commas.
Make sure you only return the keywords and say nothing else.
Do not provide additional context
For example, don't say: 
"Here are the keywords present in the document"
[/INST]

"""
prompt = example_prompt + kw_prompt


# llm = TextGeneration(generator, prompt=prompt)

#Bedrock llm for keybert
modelId = "mistral.mistral-7b-instruct-v0:2"
#client=bedrock
llm = Bedrock(model_id=modelId, credentials_profile_name="dd-sandbox-jp", model_kwargs={"temperature":0.1, })

chain = load_qa_chain(llm, chain_type = "stuff")

llm = LangChain(chain)

kw_model = KeyLLM(llm)




#Load the svm model
# with open("./classifier/svm_classifier.pkl", "rb") as infile:
#     clf = pickle.load(infile)


@app.get("/")
def get_root():
    return "test"


@app.post("/extract")
def extract_keywords(document:Dict) -> Dict:

    '''
    Pass a transcript to extract the keywords
    Purpose is to identify if answers contain key values to feed into the answers list.
    '''
    docs = []
    #Pass a document as a list to the llm
    docs.append(document['transcript'])
    keywords = kw_model.extract_keywords(docs)[0]
    L_keywords = [e.lower() for e in keywords]
    print(L_keywords)
    #now feed the keywords into the Other prompts
    emergency_type = classify_emergency(L_keywords).lstrip()

    questions = return_questions(emergency_type)
    print(questions)
    #now construct the return

    actions = suggest_service(emergency_type).lstrip()

    print(actions)
    output = {
        "questions":questions,
        "Emergency Type":emergency_type,
        "Actions":actions
        #"keywords":keywords
    }

    return output


# @app.post("/classify")
# def classify_doc(document:Dict) -> str:
#     '''
#     Pass a transcript to classify the type of emergency, will return a single type
#     Import the trained model, and pass the document to it.

#     '''
#     emergency_type = None
#     if document['transcript']:
#         emergency_type = clf.predict(document['transcript'])

#     return emergency_type

def classify_emergency(keywords:list) -> str:
    """
    Pass the extracted keywords and classify the emergency type
    """
    modelId = "mistral.mistral-7b-instruct-v0:2"

    accept = "application/json"
    contentType = "application/json"
    examplePrompt = """
        <s>[INST]
        you are an emergency call assistant, you need to classify the type of emergency based on a set of keywords.
        keywords: ["stolen", "theft", "robbery", "burglary", "pickpocket", "shoplifting", "larceny", "mugging", "snatching", 
        "grand theft", "petty theft", "auto theft", "bike theft", "identity theft", "piracy", 
        "embezzlement", "looting", "stealing", "fraudulent appropriation", "pilferage"]
        Please only return the emergency type
        Do not describe why an emergency type was set
        For example, don't say: 
        "Here is the classification based on the keywords provided"
        [/INST]theft</s>"""

    questionPrompt = f"""
        [INST]
        you are an emergency call assistant, you need to classify the type of emergency based on a set of keywords.
        keywords: {keywords}
        Please only return the emergency type
        Do not describe why an emergency type was set
        For example, don't say: 
        "Here is the classification based on the keywords provided"
        [/INST]

        """
    prompt = examplePrompt + questionPrompt
    #services = generator(prompt,do_sample=True, top_k=50, top_p=0.95, temperature=1.0, return_full_text=False)
    body = json.dumps({
        "prompt": prompt,
        "max_tokens": 50,
        "top_p": 0.9,
        "top_k": 50,
        "temperature": 0.1
    })
    response = bedrock.invoke_model(
        modelId=modelId, 
        body=body, 
        accept=accept, 
        contentType=contentType
        )
    #return str(services[0]['generated_text'])
    return json.loads(response.get('body').read())["outputs"][0]["text"]



def return_questions(keyword:str) -> list:
    '''
    Pass a transcript of keywords
    return a set of questions to ask
    '''    
    with open('questions-type.json', 'r') as infile:
        jsondata = infile.read()

    questions = json.loads(jsondata)
    to_send = []
    #Add the core 3 questions every time
    for q in questions['emergencies']:
        if "core" in q['qtype']:
            to_send.append(q['q'])

    for q in questions['emergencies']:
        if keyword in q['qtype']:
            to_send.append(q['q'])
    
    if len(to_send) == 2:
        for q in questions['emergencies']:
            if "basic" in q['qtype']:
                to_send.append(q['q'])
    return to_send    


def suggest_service(keywords:str) -> str:
    '''
    Pass keywords to know what services to call
    Purpose is to identify the services to call based on the keywords
    '''
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

    servicePrompt = f"""
        [INST]
        based on the following keywords:
        - {keywords}
        Please tell me what emergency services should be sent separate them with commas.
        Make sure you only return the service name and say nothing else.
        For example, don't say: 
        "Here are the names of the emergency services that may be needed based on your keywords:"
        I understand that I need to call emergencies but I still want to know what services should be sent.
        please do not return any other information or disclaimer.
        [/INST]

        """
    prompt = examplePrompt + servicePrompt
    #customizedPrompt = prompt.replace('[keywords]', keywords)
    #Pass a document as a list to the llm
    # services = generator(customizedPrompt,do_sample=True, top_k=50, top_p=0.95, temperature=1.0, return_full_text=False)
    # return services[0]['generated_text']
    body = json.dumps({
        "prompt": prompt,
        "max_tokens": 100,
        "top_p": 0.9,
        "top_k": 50,
        "temperature": 0.1
    })

    response = bedrock.invoke_model(
        modelId=modelId, 
        body=body, 
        accept=accept, 
        contentType=contentType
        )
    return json.loads(response.get('body').read())["outputs"][0]["text"]

