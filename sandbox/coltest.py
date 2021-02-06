import config # Подключаем конфиг-файл config.py
import telebot # Библиотеку для работы с Telegram Bot API
from telebot import types 
import pymongo # для работы с MongoDB
from pymongo import MongoClient
import random 
import json # На всякий пожарный, библиотеку для работы с JSON
from bson.objectid import ObjectId

# bot = telebot.TeleBot(config.TOKEN) # Создаем объект бота

client = MongoClient('localhost', 27017) # Подключаемся к кластеру
db = client['matchBot'] # Берем нужную базу данных

usr = db['usr'] # Берем коллекцию с пользователями

for i in usr.find({'gender' : True}):
    print(i['first_name'])