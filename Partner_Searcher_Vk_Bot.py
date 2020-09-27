from vk_api.longpoll import VkLongPoll, VkEventType
from bs4 import BeautifulSoup as bs
from datetime import datetime
from text_book import status, age_from, age_to, gender, city, check, congratulations, do_not_worry
import vk_api
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


# Функцию отправки фото ботом
def send_photo(user_id, message, attachment=None):
    kw = {'user_id': user_id, 'message': message, 'random_id': random.randrange(10 ** 7)}
    if kw:
        kw['attachment'] = attachment
    vk_session.method('messages.send', kw)


# Функцию отправки сообщения ботом
def write_message(user_id, message, random_id):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random_id})


# Функция поиска id людей, которые подошли под запросы клиента
def search_for_partner():
    partner_response = requests.get(
        "https://api.vk.com/method/users.search",
        params={
            "access_token": access_token,
            "sort": 1,
            "count": 150,
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
        if dicts.get('is_closed') is False and dicts.get('can_access_closed') is True:
            id_list.append(dicts.get('id'))
    return id_list


# Фильтрует список id, убирает id с кол-вом фото < 3
def clean_id_with_less_photos(id_list):
    for id in id_list:
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
        if photo_json['response'].get('count') < 3:
            id_list.remove(id)
    return id_list


# Функция выводящая имя фотографии в формате для отправки во вложении к сообщению
def get_photos_name(vk_id):
    photos = []
    photo_response = requests.get(
        "https://api.vk.com/method/photos.get",
        params={
            "access_token": access_token,
            "v": 5.77,
            "owner_id": vk_id,
            "album_id": "profile",
            "extended": 1,
            "photo_sizes": 0,
        }
    )
    photo_json = photo_response.json()
    time.sleep(0.34)
    if photo_json['response'].get('count') == 3:
        for elements in photo_json['response'].get('items'):
            photo_name = 'photo' + str(elements.get('owner_id')) + '_' + str(elements.get('id'))
            photos.append(photo_name)
        return photos
    elif photo_json['response'].get('count') >= 3:
        count_likes = []
        three_names = []
        for count in photo_json['response']['items']:
            count_likes.append(count.get('likes').get('count'))
        for photo in photo_json['response']['items']:
            name = 'photo' + str(photo.get('owner_id')) + '_' + str(photo.get('id'))
            three_names.append(name)
        tup = sorted(zip(count_likes, three_names), reverse=True)[:3]
        for links in tup:
            photos.append(links[1])
        return photos


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
                    break


# Выводит в консоль информацию по полученным сообщениям
def print_information_about_message(message_text):
    print('Сообщение было доставленно в ' + str(datetime.strftime(datetime.now(), '%H:%M')))
    print(message_text)
    print('-|_|-|_|-|_|-')


# Начало поиска + функция look_for_age_from
def start_searching_age_from():
    write_message(identity, age_from, random.randint(-2147483648, 2147483647))
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            message_text = event.text.lower()
            print_information_about_message(message_text)
            criterian.append(int(message_text))
            break


# Поиск пратнера по параметру возраст до
def look_for_age_to():
    write_message(identity, age_to, random.randint(-2147483648, 2147483647))
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            message_text = event.text.lower()
            print_information_about_message(message_text)
            criterian.append(int(message_text))
            break


# Поиск по параметру пол партнера
def look_for_gender():
    write_message(identity, gender, random.randint(-2147483648, 2147483647))
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            message_text = event.text.lower()
            print_information_about_message(message_text)
            criterian.append(int(message_text))
            break


# Поиск по параметру семейное положение
def look_for_status():
    write_message(identity, status, random.randint(-2147483648, 2147483647))
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            message_text = event.text.lower()
            print_information_about_message(message_text)
            criterian.append(int(message_text))
            break


# Поиск по параметру город
def look_for_partners_city():
    write_message(identity, city, random.randint(-2147483648, 2147483647))
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            message_text = event.text.lower()
            print_information_about_message(message_text)
            criterian.append(message_text)
            break


def cycle_sending_three_photos(vk_iden):
    photo_name = get_photos_name(vk_iden)
    if photo_name is None:
        pass
    else:
        for photo in photo_name:
            send_photo(identity, '', attachment=photo)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                event.text.lower()
                if event.text == 'да':
                    if event.from_user:
                        write_message(identity, 'https://vk.com/id' + str(id) + congratulations,
                                      random.randint(-2147483648, 2147483647))
                        break
                elif event.text == 'нет':
                    if event.from_user:
                        write_message(identity, do_not_worry, random.randint(-2147483648, 2147483647))
                        break


criterian = []
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        event.text.lower()
        if event.from_user:
            identity = event.user_id
            start_conversation_greetings()
            start_searching_age_from()
            look_for_age_to()
            look_for_gender()
            look_for_partners_city()
            look_for_status()
            print('Критерии отобранные клиентом', criterian)
            all_partners = search_for_partner()
            truely_partners = clean_id_with_less_photos(all_partners)
            write_message(identity, check, random.randint(-2147483648, 2147483647))
            for id in truely_partners:
                cycle_sending_three_photos(id)
                print('Фото отправлены')


