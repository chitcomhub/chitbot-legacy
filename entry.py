# Бот написан на Python 3.7

import requests
import configurations # содержит токен

# добавление данных в DynamoDB
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('top')


def point(event, context):
	print(event)

	message_text = event["message"]["text"]
	chat_id = event["message"]["chat"]["id"]
	chiter = event["message"]["from"]["username"]

	# главные команды
	if message_text[0] == "/":
		words = event["message"]["text"].split()
		command = words[0][1:]
		if command == "start":
			start_text = "Начнем турнир по программированию"
			send_message(chat_id, start_text)
		elif command == "tasks":
			for i in tasks:
				tasks_text = "%s: \n %s" % (i[1], i[2])
				send_message(chat_id, tasks_text)
		elif command == "top":
			
			# достаем из БД DynamoDB таблицу top
			response = table.scan()
			items = response['Items']

			# функция сортирует по столбцу points
			def get_key(key):
				return key['points']

			sorted_items = sorted(items, key = get_key, reverse = True)

			text = 'Рейтинг программистов:\n\n№ | Никнейм | Имя | Баллы\n\n'
			n = 0
			for i in sorted_items:
				print(i)
				n += 1
				text += " %s  | @%s | %s | %s\n" % (n,
					i['nickname'],
					i['name'],
					i['points'])

			send_message(chat_id, '%s' % text.strip())

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