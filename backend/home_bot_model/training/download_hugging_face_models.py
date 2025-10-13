import os

from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

login(token=os.getenv('HUGGING_FACE_TOKEN'))

model_name = "meta-llama/Llama-3.1-8B-Instruct"
save_path = "./models/llama-3.1-8b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=True)
model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=True)

model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)