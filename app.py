# import quart.flask_patch

import os
import time
import json
import asyncio
from quart import Quart, request, render_template, redirect, session, websocket

from chatbot import ChatBot

app = Quart(__name__)
app.config.from_file("conf.json", json.load)
app.secret_key = app.config['BOTSECRET']

chatbot = ChatBot()

@app.route('/', methods=['GET', 'POST'])
async def home():
	if session.get('username'):
		return redirect('/chat')
	elif request.method == 'GET':
		return await render_template('homepage.html')
	elif request.method == 'POST':
		req_post = await request.form
		if 'username' in req_post and str(req_post['username']).strip()!='':
			session['username'] = str(req_post['username']).strip()
			return redirect('/chat')
	else:
		return '<h1>Invalid HTTP method</h1>', 400

@app.route('/chat', methods=['GET'])
async def startchat():
	if session.get('username'):
		return await render_template('chatroom.html', username=session['username'])
	else:
		return redirect('/')

@app.route('/logout', methods=['GET'])
async def logout():
	session.pop('username')
	return redirect('/')

@app.websocket('/bot')
async def chatsocket():
	if session.get('username'):
		while True:
			data = await websocket.receive()
			await websocket.send(f"[REPLY]{data}")
	else:
		return 'Forbidden', 403

app.run()