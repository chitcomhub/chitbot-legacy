import requests
import sqlite3
import configurations # содержит токен

# соединение с SQLite3
def create_connection():
	conn = sqlite3.connect("champ.db")
	cursor = conn.cursor()
	sql = "SELECT rowid, * FROM tasks ORDER BY title"
	tasks = [row for row in cursor.execute(sql)]
	conn.close()
	return(tasks)

def point(event, context):
	print(event)
	message_text = event["message"]["text"]
	chat_id = event["message"]["chat"]["id"]
	chiter = event["message"]["from"]["username"]
	tasks = create_connection()

	# главные команды
	if message_text[0] == "/":
		words = event["message"]["text"].split()
		command = words[0][1:]
		if command == "start":
			champ_text = "Начнем турнир по программированию"
			send_message(chat_id, champ_text)
		elif command == "tasks":
			for i in tasks:
				task = "%s: \n %s" % (i[1], i[2])
				send_message(chat_id, task)
		elif command == "help":
			help_text = "Вы можете решать задачи на любом языке программирования"
			send_message(chat_id, help_text)
	
	# сравнение ответов
	for i in tasks:
		answers = "%s%s:%s" % ("task_", i[0], i[3])
		if message_text == answers:
			answer = "Участник @%s решил Задачу №%s\nОтвет: %s" % (chiter, i[0], i[3])
			send_message(chat_id, answer)

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