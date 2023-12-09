import sys
import threading
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import requests
import json
from websockets.sync.client import connect
import websockets

websocket = None
async def send_dm(bot, id, msg, send_file = False):
		member = await bot.fetch_user(id)
		if member != None:
			channel = await member.create_dm()
			if send_file:
				#r = requests.get("https://raw.githubusercontent.com/MrRGnome/PayMeBTC/master/client/client.html")
				#r.text
				#await channel.send(msg, file=discord.File(r.text, 'PayMeBTC.html'))
				await channel.send(msg)
			else:
				await channel.send(msg)
			return

async def listen(bot, og_loop):
	global websocket
	print("Starting IPC Watch")
	if(os.getenv('ENABLE_TIPS') == "1"):
		websocket = connect(os.getenv('TIPS_WEBSOCKET'))
		#there's a race condition here, websocket may not be connected in 5 seconds or may be entirely unavailable regardless. It will try again.
		await asyncio.sleep(5)
		while(1):
			try:
				message = websocket.recv()
				print(f"Received: {message}")
				try:
					msg = json.loads(message)
					if not "id" in msg and not "action" in msg:
						print("Invalid message missing id and action fields")
						continue
					if msg["action"] == "registered":
						dm = asyncio.run_coroutine_threadsafe(send_dm(bot, msg["id"], msg["msg"], True), og_loop)
						dm.result()
					elif "requestID" in msg and "amount" in msg and msg["action"] == "user_unregistered":
						sender = asyncio.run_coroutine_threadsafe(bot.fetch_user(msg["requestId"]), og_loop).result()
						receiver = asyncio.run_coroutine_threadsafe(bot.fetch_user(msg["id"]), og_loop).result()
						msg1 = receiver.name + " is not currently registered using the `" + os.getenv('BOT_PREFIX') + "register` command on the PayMeBTC Bitcoin tip bot. We have sent them a DM letting them know you are trying to tip them."
						msg2 = sender.name + " is trying to tip you " + msg["amount"] + " satoshi but they can't because you have not registered on the Bitcoin Discord tip bot. Type `" + os.getenv('BOT_PREFIX') + "register` to begin. The tip bot is non-custodial, self hosted, and interfaces with your lightning node. When you register you'll be given a link and setup instructions. You can verify this bot and DM by comparing its user ID to the user ID of BitcoinChat on the Bitcoin discord at <https://bitcointech.help>"
						dm1 = asyncio.run_coroutine_threadsafe(send_dm(bot, msg["requestId"], msg1), og_loop).result()
						dm2 = asyncio.run_coroutine_threadsafe(send_dm(bot, msg["id"], msg2), og_loop).result()
					elif "amount" in msg and msg["action"] == "user_offline":
						sender = asyncio.run_coroutine_threadsafe(bot.fetch_user(msg["requestId"]), og_loop).result()
						receiver = asyncio.run_coroutine_threadsafe(bot.fetch_user(msg["id"]), og_loop).result()
						msg1 = receiver.name + " is offline and unable to respond, but we've sent them a message reminding them to come back online and queued your tip request until they do."
						msg2 = sender.name + " is trying to send you " + msg["amount"] + " satoshi but can't because your PayMeBTC server is offline. Please restart PayMeBTC.html or re-register with the  `" + os.getenv('BOT_PREFIX') + "register` command."
						dm1 = asyncio.run_coroutine_threadsafe(send_dm(bot, msg["requestId"], msg1), og_loop).result()
						dm2 = asyncio.run_coroutine_threadsafe(send_dm(bot, msg["id"], msg2), og_loop).result()

					elif "msg" in msg:
						dm = asyncio.run_coroutine_threadsafe(send_dm(bot, msg["id"], msg["msg"]), og_loop)
						dm.result()
				except Exception as ex:
					
					print("IPC processing message error on line " + str(sys.exc_info()[-1].tb_lineno) + ": " + str(ex) + " message: " + message)
			except (websockets.exceptions.ConnectionClosed, websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK, UnboundLocalError) as ex:
				print("ipc watch failure " + str(ex))
				disconnected = True
				while disconnected:
					await asyncio.sleep(5)
					try:
						websocket = connect(os.getenv('TIPS_WEBSOCKET'))
						disconnected = False
					except Exception as ex:
						print("ipc reconnect fail " + str(ex))
			except Exception as ex:
				print("ipc watch fail " + str(ex))

