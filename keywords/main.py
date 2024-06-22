from fastapi import FastAPI
from typing import List, Dict
import json
import pickle
from keybert.llm import TextGeneration
from keybert import KeyLLM

from ctransformers import AutoModelForCausalLM
from transformers import pipeline, AutoTokenizer

from huggingface_hub import login

HFToken = json.load(open("huggingFaceToken.json"))["token"]

login(token=HFToken) 
app = FastAPI()

#Setup the llm
model = AutoModelForCausalLM.from_pretrained("../../../models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
                                             model_type="mistral",
                                             gpu_layers=0,
                                             hf=True) 

#Tokeniser from hugging face model
tokenizer = AutoTokenizer.from_pretrained("mistralai/mistral-7b-instruct-v0.1")

#Pipeline
generator = pipeline(model=model,
                     tokenizer=tokenizer,
                     task='text-generation',
                     max_new_tokens=500,
                     repetition_penalty=1.1)



example_prompt = """
<s>[INST]
I have the following document: 
- The website mentions that it only takes a couple of days to deliver but I still have not received mine.

Please give me the keywords that are present in this document and separate them with commas.
Make sure you only return the keywords and say nothing else.
For example, don't say: 
"Here are the keywords present in the document"
[/INST] potato, badger, kestral, concept, class</s>"""

kw_prompt = """
[INST]
I have the following document:
- [DOCUMENT]
Please give me the keywords that are present in this document and separate them with commas.
Make sure you only return the keywords and say nothing else.
For example, don't say: 
"Here are the keywords present in the document"

[/INST]

"""
prompt = example_prompt + kw_prompt

llm = TextGeneration(generator, prompt=prompt)
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
    keywords = kw_model.extract_keywords(docs)
    print(keywords)
    #now feed the keywords into the Other prompts
    emergency_type = classify_emergency(keywords)

    questions = return_questions(emergency_type)
    print(questions)
    #now construct the return

    actions = suggest_service(emergency_type)

    print(actions)
    output = {
        "questions":questions,
        "Emergency Type":emergency_type,
        "Actions":actions
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
    examplePrompt = """
        <s>[INST]
        you are an emergency call assistant, you need to classify the type of emergency based on a set of keywords.
        keywords: ["stolen", "theft", "robbery", "burglary", "pickpocket", "shoplifting", "larceny", "mugging", "snatching", 
        "grand theft", "petty theft", "auto theft", "bike theft", "identity theft", "piracy", 
        "embezzlement", "looting", "stealing", "fraudulent appropriation", "pilferage"]
        Please only return the emergency type
        For example, don't say: 
        "Here is the classification based on the keywords provided"
        [/INST]Theft</s>"""

    questionPrompt = f"""
        [INST]
        you are an emergency call assistant, you need to classify the type of emergency based on a set of keywords.
        answer: Theft
        keywords: {keywords}
        Please only return the emergency type
        For example, don't say: 
        "Here is the classification based on the keywords provided"
        [/INST]

        """
    prompt = examplePrompt + questionPrompt
    services = generator(prompt,do_sample=True, top_k=50, top_p=0.95, temperature=1.0, return_full_text=False)
    return str(services[0]['generated_text'])



def return_questions(keyword:str) -> list:
    '''
    Pass a transcript of keywords
    return a set of questions to ask
    '''
    #TODO: update question set.
    questions = [{'q':'What is your emergency?', 'qtype': ['basic']},
    {'q':'Where are you located right now?', 'qtype': ['basic']},
    {'q':'Can you provide the address or nearest intersection?', 'qtype': ['basic']},
    {'q':'Are you calling from a mobile phone or a landline?', 'qtype': ['basic']},
    {'q':'How many people are involved or injured?', 'qtype': ['basic']},
    {'q':'Is anyone in immediate danger?', 'qtype': ['basic']},
    {'q':'Are there any weapons involved or present at the scene?', 'qtype': ['basic']},
    {'q':'Is the situation still ongoing, or has it already occurred?', 'qtype': ['basic']},
    {'q':'Is the person conscious and breathing?', 'qtype': ['basic']},
    {'q':'Do you know CPR or any first aid that could be administered?', 'qtype': ['basic']},
    {'q':'Is there anything else important responders should know?', 'qtype': ['basic']},
    {'q':'What is your emergency?', 'qtype':['robbery']},
    {'q':'Where is the location of the robbery?', 'qtype':['robbery']},
    {'q':'Can you describe the suspects?', 'qtype':['robbery']},
    {'q':'Do you know if the suspects are still at the scene?', 'qtype':['robbery']},
    {'q':'Are there any injuries?', 'qtype':['robbery']},
    {'q':'Did you see or hear anything else that might be relevant?', 'qtype':['robbery']},
    {'q':'Is anyone else with you?', 'qtype':['robbery']},
    {'q':'Are the suspects still armed?', 'qtype':['robbery']},
    {'q':'Are you in a safe place now?', 'qtype':['robbery']},
    {'q':'Have the suspects made any demands or threats?', 'qtype':['robbery']},
    {'q':'Can you lock yourself in a secure room or area?', 'qtype':['robbery']},
    {'q':'Are there security cameras in the area that might have captured the incident?', 'qtype':['robbery']},
    {'q': 'What is your emergency?', 'qtype': ['suspicious person']},
    {'q': 'Where is the location of the suspicious person?', 'qtype': ['suspicious person']},
    {'q': 'Can you describe the suspicious person?', 'qtype': ['suspicious person']},
    {'q': 'What is the person doing that makes them suspicious?', 'qtype': ['suspicious person']},
    {'q': 'Is the person alone, or are there others with them?', 'qtype': ['suspicious person']},
    {'q': 'Do you feel threatened or unsafe because of this person\'s behavior?', 'qtype': ['suspicious person']},
    {'q': 'Has the person approached you or anyone else?', 'qtype': ['suspicious person']},
    {'q': 'Do you know if the person is armed?', 'qtype': ['suspicious person']},
    {'q': 'Have you seen the person before in the area?', 'qtype': ['suspicious person']},
    {'q': 'Are there any specific actions or statements made by the person that concern you?', 'qtype': ['suspicious person']},
    {'q': 'Have you observed the person entering or leaving any buildings or vehicles?', 'qtype': ['suspicious person']},
    {'q': 'Are there any security cameras in the area that might have captured the person\'s activities?', 'qtype': ['suspicious person']},
    {'q':'What is your emergency?', 'qtype':['domestic violence']},
    {'q':'Are you in a safe place right now?', 'qtype':['domestic violence']},
    {'q':'Is anyone injured?', 'qtype':['domestic violence']},
    {'q':'Can you tell me what happened?', 'qtype':['domestic violence']},
    {'q':'Who is the perpetrator?', 'qtype':['domestic violence']},
    {'q':'Is the perpetrator still present?', 'qtype':['domestic violence']},
    {'q':'Is there a weapon involved?', 'qtype':['domestic violence']},
    {'q':'Have there been previous incidents of violence?', 'qtype':['domestic violence']},
    {'q':'Are there children or other vulnerable individuals present?', 'qtype':['domestic violence']},
    {'q':'Do you have a safe place to go if you need to leave?', 'qtype':['domestic violence']},
    {'q':'Have you contacted any friends, family members, or support services for assistance?', 'qtype':['domestic violence']},
    {'q':'Would you like to speak with a counselor or advocate for additional support?', 'qtype':['domestic violence']},
    {'q':'Is there anything else you think is important for responders to know?', 'qtype':['domestic violence']}
    ]
    to_send = []
    for q in questions:
        if keyword in q['qtype']:
            to_send.append(q['q'])
        
    if len(to_send) == 0:
        for q in questions:
            if "basic" in q['qtype']:
                to_send.append(q['q'])
    return to_send    


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