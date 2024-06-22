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


@app.get("/")
def get_root():
    return "test"


@app.post("/service")
def suggest_service(keywords:str) -> str:
    '''
    Pass keywords to know what services to call
    Purpose is to identify the services to call based on the keywords
    '''
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
    customizedPrompt = prompt.replace('[keywords]', keywords)
    #Pass a document as a list to the llm
    services = generator(customizedPrompt,do_sample=True, top_k=50, top_p=0.95, temperature=1.0, return_full_text=False)
    return services[0]['generated_text']

@app.post("/chatbot")
def chatbot(question:str, keywords:str, answer:str) -> str:
    '''
    Pass a transcript to extract the keywords
    Purpose is to identify if answers contain key values to feed into the answers list.
    '''
    examplePrompt = """
        <s>[INST]
        I work for answering emergency calls, I need to ask the right questions to get the right information.
        based on the following question: what is your emergency?
        answer: My house is burning down.
        and keywords: burning, house.
        Please tell me what would be the best next question to ask.
        Please only return the question.
        please return only one question.
        Please use all the information provided to generate the next question.
        For example, don't say: 
        "Here is the next question you would need to ask based on your question, answer and keywords:"
        I understand that I need to call emergencies but I still want to know what services should be sent.
        [/INST]what is your location?</s>"""

    questionPrompt = """
        [INST]
        I work for answering emergency calls, I need to ask the right questions to get the right information.
        based on the following question: [question]
        answer: [answer]
        and keywords: [keywords]
        Please tell me what would be the best next question to ask.
        Please only return the question.
        please return only one question.
        Please use all the information provided to generate the next question.
        For example, don't say: 
        "Here is the next question you would need to ask based on your question, answer and keywords:"
        please do not return any other information or disclaimer.
        [/INST]

        """
    prompt = examplePrompt + questionPrompt
    customizedQuestionPrompt = prompt.replace('[keywords]', keywords).replace('[question]', question).replace('[answer]', answer)
    services = generator(customizedQuestionPrompt,do_sample=True, top_k=50, top_p=0.95, temperature=1.0, return_full_text=False)
    return services[0]['generated_text']
