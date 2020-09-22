from vk_api.longpoll import VkLongPoll, VkEventType
from bs4 import BeautifulSoup as bs
from datetime import datetime
from text_book import status, age_from, age_to, gender, city
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


# Функцию отправки письма ботом
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
        if not dicts.get('is_closed'):
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
                photo_name = 'photo-' + str(links.get('owner_id')) + '_' + str(links.get('id'))
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
                name = 'photo-' + str(photo.get('owner_id')) + '_' + str(photo.get('id'))
                three_names.append(name)
            tup = sorted(zip(photo_links, count_likes, three_names), reverse=True)[:3]
            for links in tup:
                names.append(links[2])
            return names


# Функция, сохраняющая фото на сервере??? Не очень понимаю нужна ли она все таки или нет.
# В документации размыто написанно
def saving_photos_to_server_of_vk():
    photo_response = requests.get(
        "https://api.vk.com/method/photos.getMessagesUploadServer",
        params={
            "access_token": access_token,
            "peer_id": event.user_id,
            "v": 5.52
        }
    )
    res = photo_response.json()
    download_url = res.get('upload_url')
    return download_url


# Функция скидывает только ссылку, нужна фотография
def send_photo_message(user_id, message, random_id, attachment):
    for photos in get_photos_name():
        vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random_id,
                                            'attachment': attachment})


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
                                                                        for photos in get_photos_name():
                                                                            send_photo_message(event.user_id,
                                                                                               'Нравится ли вам внешность?',
                                                                                               random.randint
                                                                                               (-2147483648,
                                                                                                2147483647), photos)
                                                                    elif event.from_chat:
                                                                        for photos in get_photos_name():
                                                                            send_photo_message(event.user_id,
                                                                                               'Нравится ли вам внешность?',
                                                                                               random.randint
                                                                                               (-2147483648,
                                                                                                2147483647), photos)
                                                                    for event in longpoll.listen():
                                                                        if event.type == VkEventType.MESSAGE_NEW and \
                                                                                event.to_me and event.text:
                                                                            print('Сообщение было доставленно в ' + str(
                                                                                datetime.strftime(datetime.now(),
                                                                                                  '%H:%M')))
                                                                            print('Текст сообщение: ' + event.text)
                                                                            print('-|_|-|_|-|_|-')
                                                                            response = event.text.lower()
                                                                            if event.text == 'да':
                                                                                print('Поздравляю это ваш партнёр')



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
