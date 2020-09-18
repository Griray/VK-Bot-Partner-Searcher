from vk_api.longpoll import VkLongPoll, VkEventType
from bs4 import BeautifulSoup as bs
from datetime import datetime
from text_book import status, age_from, age_to, gender, city, process
import vk_api
import requests
import random

token = input('Type here token ')
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
text_book_sentances = [age_from, age_to, gender, city, status, process]


def get_vk_name(user_id):
    name_response = requests.get('https://vk.com/id' + str(user_id))
    bs_response = bs(name_response.text, 'html.parser')
    name = bs_response.find('h2', class_='op_header').text
    return name.split()[0]


def write_message(user_id, message, random_id):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random_id})

criterian = []
while True:
    flag = 0
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            print('Сообщение было доставленно в ' + str(datetime.strftime(datetime.now(), '%H:%M')))
            print('Текст сообщение: ' + event.text)
            print('-|_|-|_|-|_|-')
            event.text.lower()
            if event.text == 'привет' or event.text == 'здравствуйте' or event.text == 'здравствуй':
                if event.from_user:
                    write_message(event.user_id, 'Здравствуйте, ' + get_vk_name(event.user_id) + '! ' +
                                  'Вы хотите найти себе пару?', random.randint(-2147483648, 2147483647))
                elif event.from_chat:
                    write_message(event.user_id, 'Здравствуйте, ' + get_vk_name(event.user_id) + '! ' +
                                  'Вы хотите найти себе пару?', random.randint(-2147483648, 2147483647))
                flag = 1
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                        print('Сообщение было доставленно в ' + str(datetime.strftime(datetime.now(), '%H:%M')))
                        print('Текст сообщение: ' + event.text)
                        print('-|_|-|_|-|_|-')
                        response = event.text.lower()
                        if event.text == 'да':
                            if event.from_user:
                                write_message(event.user_id, age_from, random.randint(-2147483648, 2147483647))
                            elif event.from_chat:
                                write_message(event.user_id, age_from, random.randint(-2147483648, 2147483647))
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                                    print('Сообщение было доставленно в ' + str(datetime.strftime(datetime.now(),
                                                                                                  '%H:%M')))
                                    print('Текст сообщение: ' + event.text)
                                    print('-|_|-|_|-|_|-')
                                    response = event.text.lower()
                                    criterian.append(int(response))
                                    if event.from_user:
                                        write_message(event.user_id, age_to, random.randint(-2147483648, 2147483647))
                                    elif event.from_chat:
                                        write_message(event.user_id, age_to, random.randint(-2147483648, 2147483647))
                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                                            print('Сообщение было доставленно в ' + str(
                                                datetime.strftime(datetime.now(), '%H:%M')))
                                            print('Текст сообщение: ' + event.text)
                                            print('-|_|-|_|-|_|-')
                                            response = event.text.lower()
                                            criterian.append(int(response))
                                            if event.from_user:
                                                write_message(event.user_id, gender,
                                                              random.randint(-2147483648, 2147483647))
                                            elif event.from_chat:
                                                write_message(event.user_id, gender,
                                                              random.randint(-2147483648, 2147483647))
                                            for event in longpoll.listen():
                                                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                                                    print('Сообщение было доставленно в ' + str(
                                                        datetime.strftime(datetime.now(), '%H:%M')))
                                                    print('Текст сообщение: ' + event.text)
                                                    print('-|_|-|_|-|_|-')
                                                    response = event.text.lower()
                                                    criterian.append(int(response))
                                                    if event.from_user:
                                                        write_message(event.user_id, city,
                                                                      random.randint(-2147483648, 2147483647))
                                                    elif event.from_chat:
                                                        write_message(event.user_id, city,
                                                                      random.randint(-2147483648, 2147483647))
                                                    for event in longpoll.listen():
                                                        if event.type == VkEventType.MESSAGE_NEW and event.to_me and \
                                                                event.text:
                                                            print('Сообщение было доставленно в ' + str(
                                                                datetime.strftime(datetime.now(), '%H:%M')))
                                                            print('Текст сообщение: ' + event.text)
                                                            print('-|_|-|_|-|_|-')
                                                            response = event.text.lower()
                                                            criterian.append(response)
                                                            if event.from_user:
                                                                write_message(event.user_id, status,
                                                                              random.randint(-2147483648, 2147483647))
                                                            elif event.from_chat:
                                                                write_message(event.user_id, status,
                                                                              random.randint(-2147483648, 2147483647))
                                                            for event in longpoll.listen():
                                                                if event.type == VkEventType.MESSAGE_NEW and \
                                                                        event.to_me and event.text:
                                                                    print('Сообщение было доставленно в ' + str(
                                                                        datetime.strftime(datetime.now(), '%H:%M')))
                                                                    print('Текст сообщение: ' + event.text)
                                                                    print('-|_|-|_|-|_|-')
                                                                    response = event.text.lower()
                                                                    criterian.append(response)
                                                                    print(criterian)
                                                                    if event.from_user:
                                                                        write_message(event.user_id, process,
                                                                                      random.randint(-2147483648,
                                                                                                     2147483647))
                                                                    elif event.from_chat:
                                                                        write_message(event.user_id, process,
                                                                                      random.randint(-2147483648,
                                                                                                     2147483647))
            elif event.text == 'пока' or event.text == 'до свидания':
                if event.from_user:
                    write_message(event.user_id, 'Всего доброго, ' + get_vk_name(event.user_id) + ')',
                                  random.randint(-2147483648, 2147483647))
                elif event.from_chat:
                    write_message(event.user_id, 'Всего доброго, ' + get_vk_name(event.user_id) + ')',
                                  random.randint(-2147483648, 2147483647))
            else:
                if event.from_user:
                    write_message(event.user_id, 'Я еще не научился отвечать на такие предложения)',
                                  random.randint(-2147483648, 2147483647))
                elif event.from_chat:
                    write_message(event.user_id, 'Я еще не научился отвечать на такие предложения)',
                                  random.randint(-2147483648, 2147483647))