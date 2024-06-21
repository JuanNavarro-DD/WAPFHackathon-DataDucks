from fastapi import FastAPI
from typing import List, Dict
import json
import pickle
from keybert.llm import TextGeneration
from keybert import KeyLLM

from ctransformers import AutoModelForCausalLM
from transformers import pipeline, AutoTokenizer

app = FastAPI()

#Setup the llm
model = AutoModelForCausalLM.from_pretrained("../../../models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
                                             model_type="mistral",
                                             gpu_layers=0,
                                             hf=True) 

#Tokeniser from hugging face model
tokenizer = AutoTokenizer.from_pretrained(model) #TODO: fix

#Pipeline
generator = pipeline(model=model,
                     #tokenizer=tokenizer,
                     task='text-generation',
                     max_new_tokens=50,
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
def extract_keywords(document:Dict) -> List:
    '''
    Pass a transcript to extract the keywords
    Purpose is to identify if answers contain key values to feed into the answers list.
    '''
    docs = []
    #Pass a document as a list to the llm
    docs.append(document['transcript'])
    keywords = kw_model.extract_keywords(docs)
    return keywords


@app.post("/classify")
def classify_doc(document:Dict) -> str:
    '''
    Pass a transcript to classify the type of emergency, will return a single type
    Import the trained model, and pass the document to it.

    '''
    emergency_type = None
    if document['transcript']:
        emergency_type = clf.predict(document['transcript'])

    return emergency_type

