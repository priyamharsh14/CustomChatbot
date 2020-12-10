import time
import asyncio
from quart import Quart, websocket, request, render_template

from chatbot import ChatBot

app = Quart(__name__)
chatbot = ChatBot()

@app.route('/', methods=['GET'])
async def homepage():
	return await 'HOMEPAGE'

app.run(host="34.87.31.38", port=5000)