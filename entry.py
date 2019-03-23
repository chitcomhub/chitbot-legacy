# Бот написан на Python 3.7

import requests
import configurations # содержит токен и id группы
import boto3

def point(event, context):
	print(event)

	dynamodb = boto3.resource('dynamodb')
	top_table = dynamodb.Table('top')
	tasks_table = dynamodb.Table('tasks')

	# достаем из БД DynamoDB таблицу tasks
	response = tasks_table.scan()
	tasks_items = response['Items']

	# достаем из БД DynamoDB таблицу top
	response = top_table.scan()
	top_items = response['Items']

	message_text = event["message"]["text"]
	chat_id = event["message"]["chat"]["id"]
	username = event["message"]["from"]["username"]
	user_id = event["message"]["from"]["id"]
	name = event["message"]["from"]["first_name"]

	if chat_id != configurations.group_id:
		send_message(chat_id, "Мне запрещено общаться вне группы CHITCOM")
		raise Exception('Попытались мне написать в чате: ' + str(chat_id))

	if message_text == "reg_me":
		this_user = True
		for i in top_items:
			if int(user_id) == i['id']:
				send_message(chat_id, 'Ты уже ранее был зарегистрирован\nСмотри в /top')
				this_user = False
				break
		
		if this_user == True:
			top_table.put_item(
			   Item={
			   		'id' : user_id,
			        'nickname': username,
			        'name': name,
			        'points': 0
			    }
			)
			send_message(chat_id, "Я занес вас в список участников\nСмотри в /top")

	# главные команды
	elif message_text[0] == "/":
		words = event["message"]["text"].split()
		command = words[0][1:]
		if command == "start" or command == "start@chit_champ_bot":
			start_text = """
					Начнем турнир по программированию CHIT CHAMP.
				Но прежде, чем ты начнешь выполнять задачи,
				в кратце объясню что это за турнир и какие на нем правила.
				Турнир расчитан на то, чтобы определить сильнейших
				программистов в CHITCOM комьюнити.

					Правила:
				1. Для начала надо зарегистрироваться.
					просто отправь мне текст reg_me
					После этого ты сможешь себя увидеть в рейтинге,
					отправив мне /top
				3. /top - это рейтинг программистов.
					Чтобы ты был на высоте,
					тебе нужно набирать баллы,
					выполняя задачи.
				4. /task - задачи, которые тебе придется решить.
					За каждое выполненную задачу ты получаешь 1 балл.
					Главное, побыстрее выполнить все задачи,
					так как балл забирает тот, кто первым выполнит задачу.

					Стань победителем CHIT CHAMP и выиграй 1.000.000.000 рублей (нет).
				Ты получишь мотивацию развиваться, как программист."""

			send_message(chat_id, start_text)

		elif command == "task" or command == "task@chit_champ_bot":

			# функция сортирует по столбцу id
			def get_key(key):
				return key['id']

			sorted_items = sorted(tasks_items, key = get_key)

			end_game = True
			for i in sorted_items:
				if i['winner'] == "0":
					tasks_text = "Задача №%s: \n\t%s\n\n" % (i['id'], i['task'])
					send_message(chat_id, tasks_text)
					end_game = False
					break
			if end_game == True:
				end_text = """Турнир окончен.
				Наберите /top, чтобы увидеть рейтинг программистов"""
				send_message(chat_id, end_text)

		elif command == "top" or command == "top@chit_champ_bot":

			# функция сортирует по столбцу points
			def get_key(key):
				return key['points']

			sorted_items = sorted(top_items, key = get_key, reverse = True)

			top_text = 'Рейтинг программистов:\n\n№ | Никнейм | Имя | Баллы\n\n'
			n = 0
			for i in sorted_items:
				n += 1
				top_text += " %s  | @%s | %s | %s\n" % (n,
					i['nickname'],
					i['name'],
					i['points'])

			send_message(chat_id, '%s' % top_text.strip())

	# сравнение ответов
	else:
		for i in tasks_items:
			solution = "%s%s:%s" % ('task', i['id'], i['solution'])
			if message_text.replace(' ', '') == solution and i['winner'] == '0':
				answer = """@%s решил Задачу №%s и получил 1 балл.
					Решение: %s.
					Чтоб перейти на следующее задание, введите /task
					""" % (username, i['id'], i['solution'])

				# добавляем правильно ответившего в поле winner
				tasks_table.update_item(
				    Key={
				        'id': i['id']
				    },
				    UpdateExpression='SET winner = :val1',
				    ExpressionAttributeValues={
				        ':val1': username
				    }
				)

				# добавляем балл за верный ответ
				for i in top_items:
					if i['id'] == int(user_id):
						point = i['points']

				top_table.update_item(
				    Key={
				        'id': user_id
				    },
				    UpdateExpression='SET points = :val1',
				    ExpressionAttributeValues={
				        ':val1': point + 1
				    }
				)

				send_message(chat_id, answer)
				break

			elif message_text.replace(' ', '') == solution:
				answer = """Эту задачу уже решил @%s.
					Решение: %s.
					Вы должны решить уже следующую задачу.
					Чтоб перейти к действующей задаче, введите /task
					""" % (i['winner'], i['solution'])

				send_message(chat_id, answer)
				break


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