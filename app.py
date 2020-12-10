import time
import asyncio
from quart import Quart, websocket, request, render_template
from transformers import OpenAIGPTLMHeadModel, OpenAIGPTTokenizer, GPT2LMHeadModel, GPT2Tokenizer

from chatbot import generate_reply
from train import add_special_tokens_
from utils import get_dataset, download_pretrained_model

app = Quart(__name__)

print("[+] Loading pretrained model.. ", end="")
model_checkpoint = download_pretrained_model()
tokenizer_class, model_class = (OpenAIGPTTokenizer, OpenAIGPTLMHeadModel)
tokenizer = tokenizer_class.from_pretrained(model_checkpoint)
model = model_class.from_pretrained(model_checkpoint)
_device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(_device)
print("DONE")

print("[+] Adding special tokens.. ", end="")
add_special_tokens_(model, tokenizer)
print("DONE")

if not os.path.isfile("./dataset_cache" + '_' + type(tokenizer).__name__):
	print("[!] NOTE: THE FOLLOWING PROCESS WILL TAKE SOME TIME.")
	print("[!] NOTE: DO NOT EXIT THE PROGRAM DURING THE PROCESS.")
print("[+] Loading dataset.. ", end="")
dataset = get_dataset(tokenizer, "", "./dataset_cache")
print("DONE")

@app.route('/', methods=['GET'])
async def homepage():
	return await 'HOMEPAGE'

app.run()