from cgitb import text
import json
from fastapi import FastAPI
from ctransformers import AutoModelForCausalLM
from transformers import pipeline, AutoTokenizer
from huggingface_hub import login

HFToken = json.load(open("huggingFaceToken.json"))["token"]

login(token=HFToken) 

app = FastAPI()

modelPath = "models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"

#Setup the llm
model = AutoModelForCausalLM.from_pretrained(modelPath,
                                             model_type="mistral",
                                             gpu_layers=0,
                                             hf=True) 

#Tokeniser from hugging face model
tokenizer = AutoTokenizer.from_pretrained("mistralai/mistral-7b-instruct-v0.1")

#Pipeline
generator = pipeline(model=model,
                     tokenizer=tokenizer,
                     task='text-generation',
                     max_new_tokens=50,
                     repetition_penalty=1.1)


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



# llm = TextGeneration(generator, prompt=prompt)
# kw_model = KeyLLM(llm)

#Load the svm model
# with open("./classifier/svm_classifier.pkl", "rb") as infile:
#     clf = pickle.load(infile)


@app.get("/")
def get_root():
    return "test"


@app.post("/service")
def suggest_service(keywords:str) -> str:
    '''
    Pass a transcript to extract the keywords
    Purpose is to identify if answers contain key values to feed into the answers list.
    '''
    customizedPrompt = prompt.replace('[keywords]', keywords)
    #Pass a document as a list to the llm
    services = generator(customizedPrompt,do_sample=True, top_k=50, top_p=0.95, temperature=1.0, return_full_text=False)
    return services[0]['generated_text']


