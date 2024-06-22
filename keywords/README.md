# Running

`uvicorn main:app --reload`

# Testing

`localhost:8000/docs` provides a swagger endpoint which can be used for testing

# Installing Models

- Download the 'mistral-7b-instruct-v0.1.Q4_K_M.gguf' model from hugging face https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF

- Create a hugging face account, and generate a token for collecting the tokenisation from mistralai/mistral-7b-instruct-v0.1


- Go to https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1 and accept the terms and conditions of the model

- set the path to your local model in the main.py
- create huggingFaceToken.json, in the working directory and add your hugging face token into the the json in format `{"token":"MYTOKEN"}`

