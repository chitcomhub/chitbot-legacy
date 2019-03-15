import telebot
import constants

bot = telebot.TeleBot(constants.token)

bot.send_message(168091708, "test")