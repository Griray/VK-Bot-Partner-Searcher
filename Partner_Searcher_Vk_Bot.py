from vk_api.longpoll import VkLongPoll, VkEventType
from bs4 import BeautifulSoup as bs
from datetime import datetime
from text_book import status, age_from, age_to, gender, city, check, congratulations
import vk_api
from vk_api import VkUpload
import requests
import random
import time

token = input('Type here group token ')
access_token = input('Type personal token here ')
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


# Получаем имя пользователя, который к нам обратился за поиском партнёра
def get_vk_name(user_id):
    name_response = requests.get('https://vk.com/id' + str(user_id))
    bs_response = bs(name_response.text, 'html.parser')
    name = bs_response.find('h2', class_='op_header').text
    return name.split()[0]


def get_vk_id(user_id):
    response = requests.get(
        "https://api.vk.com/method/users.get",
        params={
            "access_token": token,
            "v": 5.89,
            "user_ids": user_id,
        }
    )
    id_nick_json = response.json()
    return id_nick_json['response'][0].get('id')


# Функцию отправки фото ботом
def send_photo(user_id, message, attachment=None):
    kw = {'user_id': user_id, 'message': message, 'random_id': random.randrange(10 ** 7)}
    if kw:
        kw['attachment'] = attachment
    vk_session.method('messages.send', kw)


def write_message(user_id, message, random_id):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random_id})


# Функция поиска id людей, которые подошли под запросы елиента бота
def search_for_partner():
    partner_response = requests.get(
        "https://api.vk.com/method/users.search",
        params={
            "access_token": access_token,
            "sort": 1,
            "count": 20,
            "hometown": criterian[3],
            "sex": criterian[2],
            "status": criterian[4],
            "age_from": criterian[0],
            "age_to": criterian[1],
            "has_photo": 1,
            "v": 5.89
        }
    )
    partners = partner_response.json()
    time.sleep(0.34)
    id_list = []
    for dicts in partners['response']['items']:
        if dicts.get('is_closed') is False:
            id_list.append(dicts.get('id'))
    return id_list


# Функция на получение url фотографий подходящих партнеров, ID которых отобраны в функции search_for_partner
def get_partner_photos():
    for id in search_for_partner():
        photo_response = requests.get(
            "https://api.vk.com/method/photos.get",
            params={
                "access_token": access_token,
                "v": 5.77,
                "owner_id": id,
                "album_id": "profile",
                "extended": 1,
                "photo_sizes": 0,
            }
        )
        photo_json = photo_response.json()
        time.sleep(0.34)
        jpg_links = []
        if photo_json['response'].get('count') == 3:
            for links in photo_json['response']['items']:
                jpg_links.append(links.get('sizes')[-1].get('url'))
            return jpg_links
        elif photo_json['response'].get('count') > 3:
            photo_links = []
            count_likes = []
            for links in photo_json['response']['items']:
                photo_links.append(links.get('sizes')[-1].get('url'))
            for count in photo_json['response']['items']:
                count_likes.append(count.get('likes').get('count'))
            tup = sorted(zip(photo_links, count_likes), reverse=True)[:3]
            for links in tup:
                jpg_links.append(links[0])
            return jpg_links
        else:
            continue


# Функция выводящая имя фотографии в формате для отправки во вложении к сообщению
def get_photos_name():
    for id in search_for_partner():
        photo_response = requests.get(
            "https://api.vk.com/method/photos.get",
            params={
                "access_token": access_token,
                "v": 5.77,
                "owner_id": id,
                "album_id": "profile",
                "extended": 1,
                "photo_sizes": 0,
            }
        )
        photo_json = photo_response.json()
        time.sleep(0.34)
        names = []
        if photo_json['response'].get('count') == 3:
            for links in photo_json['response']['items']:
                photo_name = 'photo' + str(links.get('owner_id')) + '_' + str(links.get('id'))
                names.append(photo_name)
                return names
        elif photo_json['response'].get('count') > 3:
            photo_links = []
            count_likes = []
            three_names = []
            for links in photo_json['response']['items']:
                photo_links.append(links.get('sizes')[-1].get('url'))
            for count in photo_json['response']['items']:
                count_likes.append(count.get('likes').get('count'))
            for photo in photo_json['response']['items']:
                name = 'photo' + str(photo.get('owner_id')) + '_' + str(photo.get('id'))
                three_names.append(name)
            tup = sorted(zip(photo_links, count_likes, three_names), reverse=True)[:3]
            for links in tup:
                names.append(links[2])
                return names


# Функция, сохраняющая фото на сервере??? Не очень понимаю нужна ли она все таки или нет.
# В документации размыто написанно
# def saving_photos_to_server_of_vk():
#     photo_response = requests.get(
#         "https://api.vk.com/method/photos.getMessagesUploadServer",
#         params={
#             "access_token": access_token,
#             "peer_id": event.user_id,
#             "v": 5.52
#         }
#     )
#     res = photo_response.json()
#     download_url = res.get('upload_url')
#     return download_url


# Ожидает первого сообщения от пользователя
def start_conversation_greetings():
    write_message(identity, 'Здравствуйте, ' + get_vk_name(identity) + '! ' +
                  'Вы хотите найти себе пару?', random.randint(-2147483648, 2147483647))
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            message_text = event.text.lower()
            print_information_about_message(message_text)
            if event.text == 'да':
                if event.from_user:
                    write_message(identity, 'Начнём', random.randint(-2147483648, 2147483647))
                elif event.from_chat:
                    write_message(identity, 'Начнём', random.randint(-2147483648, 2147483647))
                    break
            elif event.text == 'нет':
                if event.from_user:
                    write_message(identity, 'Я другого не умею', random.randint(-2147483648, 2147483647))
                elif event.from_chat:
                    write_message(identity, 'Я другого не умею', random.randint(-2147483648, 2147483647))


# Выводит в консоль информацию по полученным сообщениям
def print_information_about_message(message_text):
    print('Сообщение было доставленно в ' + str(datetime.strftime(datetime.now(), '%H:%M')))
    print(message_text)
    print('-|_|-|_|-|_|-')


# Начало поиска + функция look_for_age_from
def start_searching_age_from():
    write_message(identity, age_from, random.randint(-2147483648, 2147483647))
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        message_text = event.text.lower()
        print_information_about_message(message_text)
        criterian.append(int(message_text))


# Поиск пратнера по параметру возраст до
def look_for_age_to():
    write_message(identity, age_to, random.randint(-2147483648, 2147483647))
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        message_text = event.text.lower()
        print_information_about_message(message_text)
        criterian.append(int(message_text))


# Поиск по параметру пол партнера
def look_for_gender():
    write_message(identity, gender, random.randint(-2147483648, 2147483647))
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        message_text = event.text.lower()
        print_information_about_message(message_text)
        criterian.append(int(message_text))


# Поиск по параметру семейное положение
def look_for_status():
    write_message(identity, status, random.randint(-2147483648, 2147483647))
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        message_text = event.text.lower()
        print_information_about_message(message_text)
        criterian.append(int(message_text))


# Поиск по параметру город
def look_for_partners_city():
    write_message(identity, city, random.randint(-2147483648, 2147483647))
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        message_text = event.text.lower()
        print_information_about_message(message_text)
        criterian.append(message_text)


criterian = []

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        event.text.lower()
        if event.from_user:
            identity = event.user_id
            start_conversation_greetings()
            start_searching_age_from()
