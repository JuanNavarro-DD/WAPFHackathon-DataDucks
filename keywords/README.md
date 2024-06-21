# Running

`uvicorn main:app --reload`

# Testing

`localhost:8000/docs` provides a swagger endpoint which can be used for testing

# Installing Models

- Download the 'mistral-7b-instruct-v0.1.Q4_K_M.gguf' model from hugging face https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF

- Create a hugging face account, and generate a token for collecting the tokenisation from mistralai/mistral-7b-instruct-v0.1

- set the path to your local model in the main.py
- set the token in the main.py (this will be an environment variable in the future)