import config # Подключаем конфиг-файл config.py
import telebot # Библиотеку для работы с Telegram Bot API
from telebot import types 
import pymongo # для работы с MongoDB
from pymongo import MongoClient
import random 
import json # На всякий пожарный, библиотеку для работы с JSON
from bson.objectid import ObjectId

bot = telebot.TeleBot(config.TOKEN) # Создаем объект бота

client = MongoClient('localhost', 27017) # Подключаемся к кластеру
db = client['matchBot'] # Берем нужную базу данных

usr = db['usr'] # Берем коллекцию с пользователями

class Person:
    def __init__(self, first_name, last_name, gender, tgid):
        self.tgid = tgid
        
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender

        self.likeInbox = [] # Лайки челу
        self.likeOutbox = [] # Те, кого чел лайкнул

    def likeBy(self, from_person):
        self.likeInbox.append(from_person.tgid)
        from_person.likeOutbox.append(self.tgid)
        if from_person.tgid in self.likeOutbox:
            # print('MATCH!', from_person.first_name, 'and', people[str(self.tgid)].first_name, 'are dancing from now!')
            bot.send_message(int(from_person.tgid), '♥️ У вас новый мэтч!')
            bot.send_message(int(self.tgid), '♥️ У вас новый мэтч!')


    def toDict(self):
        d = {}
        d['tgid'] = self.tgid

        d['first_name'] = self.first_name
        d['last_name'] = self.last_name
        d['gender'] = self.gender

        d['inbox'] = self.likeInbox
        d['outbox'] = self.likeOutbox

        return d

regdata = {}
people = {}

boysids = []
girlsids = []

findData = {}

def likesaver(message):
    u = str(message.chat.id)
    if message.text == '💔 Начать':
        # Удалить все лайки
        for i in people[u].likeOutbox:
            print('LIKESAVER', people[i].likeInbox, i)
            people[i].likeInbox.remove(u)
            usr.find_one_and_delete({'tgid' : i})
            usr.insert_one(people[i].toDict())
        
        people[u].likeOutbox = []

        # print('likesaver DEBUG', u, people[u].likeOutbox)

        usr.find_one_and_delete({'tgid' : u})
        usr.insert_one(people[u].toDict())

        if people[u].gender:
            finder_for_boys(message) # Начинаем поиск девочек, если перед нами пацан
        else:
            finder_for_girls(message) # Начинаем поиск мальчиков, если перед нами девочка
    else:
        menu(message)

def finder_for_girls(message):
    u = str(message.from_user.id)
    findData[u] += 1

    if findData[u] >= len(boysids):
        bot.send_message(message.chat.id, 'Готово! Вы прошли процедуру поиска.')
        # findData[u] = 0
        menu(message)

    # if findData[u] != 0:
    if message.text == '✅ Да':
        people[boysids[findData[u] - 1]].likeBy(people[u])
    
    if findData[u] >= len(boysids):
        usr.find_one_and_delete({'tgid' : u})
        usr.insert_one(people[u].toDict())

        for i in people[u].likeOutbox:
            usr.find_one_and_delete({'tgid' : i})
            usr.insert_one(people[i].toDict())
        return 0

    i = boysids[findData[u]]
    test = people[i]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('✅ Да'), types.KeyboardButton('🔴 Нет'))

    msg = bot.send_message(message.chat.id, 'Хотите танцевать с ' + test.first_name + ' ' + test.last_name + '?', reply_markup=markup)

    if not(findData[u] >= len(boysids) + 1):
        bot.register_next_step_handler(msg, finder_for_girls)

def finder_for_boys(message):
    u = str(message.from_user.id)
    findData[u] += 1

    if findData[u] >= len(girlsids):
        bot.send_message(message.chat.id, 'Готово! Вы прошли процедуру поиска.')
        print('Time to stop!', findData[u], len(girlsids))
        # findData[u] = 0
        menu(message)

    # if findData[u] != 0:
    if message.text == '✅ Да':
        print('Like!')
        people[girlsids[findData[u] - 1]].likeBy(people[u])
    
    if findData[u] >= len(girlsids):
        print('STOP!')
        usr.find_one_and_delete({'tgid' : u})
        usr.insert_one(people[u].toDict())

        for i in people[u].likeOutbox:
            usr.find_one_and_delete({'tgid' : i})
            usr.insert_one(people[i].toDict())
        return 0

    i = girlsids[findData[u]]
    test = people[i]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('✅ Да'), types.KeyboardButton('🔴 Нет'))

    msg = bot.send_message(message.chat.id, 'Хотите танцевать с ' + test.first_name + ' ' + test.last_name + '?', reply_markup=markup)

    if not(findData[u] >= len(girlsids) + 1):
        print('Next step registered! n =', findData[u])
        bot.register_next_step_handler(msg, finder_for_boys)

def reggender(message):
    if message.text == '🧑 Мужской':
        regdata[message.from_user.id]['gender'] = True

    elif message.text == '👩 Женский':
        regdata[message.from_user.id]['gender'] = False

    else:
        msg = bot.send_message(message.chat.id, 'Используйте одну из кнопок снизу.')
        bot.register_next_step_handler(msg, reggender)
    
    u = str(message.from_user.id)
    people[u] = Person(regdata[message.from_user.id]['first_name'], regdata[message.from_user.id]['last_name'], regdata[message.from_user.id]['gender'], u)
    if people[u].gender == False:
        girlsids.append(u)
    else:
        boysids.append(str(u))
    usr.insert_one(people[u].toDict())
    regdata[u] = None
    bot.send_message(message.chat.id, 'Вы успешно зарегистрировались!')
    print('reg done!', len(people), people[u])
    findData[u] = -1 
    menu(message)

def reglastname(message):
    regdata[message.from_user.id]['last_name'] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('🧑 Мужской'), types.KeyboardButton('👩 Женский'))

    msg = bot.send_message(message.chat.id, 'Выберите пол.', reply_markup=markup)
    bot.register_next_step_handler(msg, reggender) # Регистрируем следующий шаг, перенаправляем в функцию reggender

def regname(message):
    regdata[message.from_user.id] = {'first_name' : message.text}
    msg = bot.send_message(message.chat.id, 'Теперь введите свою фамилию.')
    bot.register_next_step_handler(msg, reglastname) # Регистрируем следующий шаг, перенаправляем в функцию reglastname

@bot.message_handler(commands=['menu','start']) # Декоратор для отлавливания новых пользователей / отображения меню
def menu(message): # Аргумент message принимает объект сообщения
    if usr.find_one({'tgid' : str(message.from_user.id)}) == None: # Нашли нового пользователя
        msg = bot.send_message(message.chat.id, 'Добро пожаловать!\nЧтобы начать поиск напарника, введите свое имя (например, Герман) Фамилию вводить пока не нужно!')
        bot.register_next_step_handler(msg, regname) # Регистрируем следующий шаг, перенаправляем в функцию regname
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(types.KeyboardButton('📄 Список пользователей'), types.KeyboardButton('🔮 Мои лайки и мэтчи'), types.KeyboardButton('🔎 Начать поиск'))

        msg = bot.send_message(message.chat.id, 'Добро пожаловать! Чтобы начать работу с ботом, выберите одну из функий ниже', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def quote(message):
    if message.text == '📄 Список пользователей':
        boys = 'Список зарегистрировавшихся юношей :\n'
        girls = 'Список зарегистрировавшихся девушек :\n'
        for i in people:
            obj = people[i]
            if obj.gender:
                boys += ('- ' + obj.first_name + ' ' + obj.last_name + '\n')
            else:
                girls += ('- ' + obj.first_name + ' ' + obj.last_name + '\n')

        msg = bot.send_message(message.chat.id, boys + '\n' + girls)

    elif message.text == '🔎 Начать поиск':
        u = str(message.from_user.id)
        findData[u] = -1

        if len(people[u].likeOutbox) == 0:
            if people[u].gender == True: # Если перед нами юноша
                if len(girlsids) > 0:
                    finder_for_boys(message)
                else:
                    bot.send_message(message.chat.id, 'Ни одна девочка еще не зарегиситрировалась!')
            
            else: # Если перед нами девушка
                if len(boysids) > 0:
                    finder_for_girls(message)
                else:
                    bot.send_message(message.chat.id, 'Ни один парень еще не зарегистрировался!')
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('💔 Начать'), types.KeyboardButton('⏹ Не начинать'))
            msg = bot.send_message(message.chat.id, 'Начало нового поиска удалит все ваши текущие лайки!\nНАЧАТЬ ПОИСК?', reply_markup=markup)
            bot.register_next_step_handler(msg, likesaver)

    elif message.text == '🔮 Мои лайки и мэтчи':
        u = str(message.from_user.id)

        ltxt = 'Ваши лайки:\n'
        mtxt = 'Ваши мэтчи:\n'

        for i in people[u].likeOutbox:
            ltxt += '- ' + people[i].first_name + ' ' + people[i].last_name + '\n'
            if i in people[u].likeInbox:
                mtxt += '- ' + people[i].first_name + ' ' + people[i].last_name + '\n'
        
        bot.send_message(message.chat.id, ltxt)
        bot.send_message(message.chat.id, mtxt)

    else:
        bot.send_message(message.chat.id, 'Команда не распознана!')

b, g = [0, 0]

for i in usr.find({'gender' : True}):
    people[i['tgid']] = Person(i['first_name'], i['last_name'], i['gender'], i['tgid'])
    people[i['tgid']].likeInbox = i['inbox']
    people[i['tgid']].likeOutbox = i['outbox']
    boysids.append(i['tgid'])
    b += 1

for i in usr.find({'gender' : False}):
    people[i['tgid']] = Person(i['first_name'], i['last_name'], i['gender'], i['tgid'])
    people[i['tgid']].likeInbox = i['inbox']
    people[i['tgid']].likeOutbox = i['outbox']
    girlsids.append(i['tgid'])
    g += 1

for i in people:
    findData[str(i)] = -1

print('=== BOT READY ===')
print('loaded', b, 'boys and', g ,'girls')

if __name__ == '__main__': # Штука, запускающая обновление бота в Online-режиме
    bot.polling(none_stop=True)