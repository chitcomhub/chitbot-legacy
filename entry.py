import requests
import configurations

def point(event, context):
	print(event)
	if event["message"]["text"][0] == "/":
		words = event["message"]["text"].split()
		command = words[0][1:]
		if command == "start":
			champ_text = "Начнем турнир по программированию."
			send_message(event["message"]["chat"]["id"], champ_text)
		elif command == "help":
			help_text = "Вы можете решать задачи на любом языке программирования."
			send_message(event["message"]["chat"]["id"], help_text)

def send_message(chat_id, text):
	url = "https://api.telegram.org/bot{token}/{method}".format(
		token=configurations.token,
		method="sendMessage"
	)
	data = {
		"chat_id": chat_id,
		"text": text
	}
	r = requests.post(url, data = data)
	print(r.json())