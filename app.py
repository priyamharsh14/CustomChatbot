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

check_params = lambda params, req_form: all(list(map(lambda x: x in req_form and str(req_form[x]).strip(), params)))

@app.route('/', methods=['GET', 'POST'])
async def home():
	if session.get('username'):
		return redirect('/chat')
	elif request.method == 'GET':
		return await render_template('homepage.html')
	elif request.method == 'POST':
		req_form = await request.form
		if check_params(['username', 'tag'], req_form) and req_form['username'].isalnum() and req_form['tag'].isalpha():
			session['username'] = req_form['username']
			session['tag'] = chatbot.tokenizer.encode(req_form['tag'])[0]
			chats_path = "chats/" + session['username'] + ".json"
			if not os.path.isfile(chats_path):
				temp = {
					'username': session['username'],
					'persona': chatbot.get_random_personality(session['tag']),
					'history': []
				}
				with open(chats_path, 'w') as fp:
					fp.write(json.dumps(temp))
			return redirect('/chat')
		else:
			return await render_template('homepage.html', error="Invalid Username or Tag")

@app.route('/chat', methods=['GET'])
async def startchat():
	if check_params(['username', 'tag'], session):
		return await render_template('chatroom.html', username=session['username'])
	else:
		return redirect('/')

@app.route('/logout', methods=['GET'])
async def logout():
	if check_params(['username', 'tag'], session):
		session.pop('username')
		session.pop('tag')
	return redirect('/')

@app.websocket('/bot')
async def chatsocket():
	if check_params(['username', 'tag'], session):
		chats_path = "chats/" + session['username'] + ".json"
		user_data = json.load(open(chats_path))
		# TODO: send some previous chat history
		try:
			while True:
				data = await websocket.receive()
				user_data, reply = chatbot.generate_reply(user_data, data)
				await websocket.send(f"[REPLY]{reply}")
		except asyncio.CancelledError:
			# chat history will be saved only if the user disconnect or logout
			with open(chats_path, 'w') as fp:
				temp = {
					"username": user_data['username'],
					"persona": user_data['persona'],
					"history": user_data['history'],
				}
				fp.write(json.dumps(temp))
			raise
	else:
		return 'Forbidden', 403

app.run()