from vk_api.longpoll import VkLongPoll, VkEventType
from datetime import datetime
from sql_models import sq
from text_book import status, age_from, age_to, gender, city, check, congratulations, do_not_worry, wait, \
    advice_for_continue_search
from sql_models import User, Partner, PhotoData, session
import vk_api
import requests
import random
import time

token = input('Type here group token ')
access_token = input('Type personal token here ')
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


# Получить имя клиента/партнера
def get_person_name(id):
    partner_response = requests.get(
        "https://api.vk.com/method/users.get",
        params={
            "access_token": token,
            "user_ids": id,
            "fields": "city,bdate,",
            "name_case": "Nom",
            "v": 5.124
        }
    )
    partners = partner_response.json()
    time.sleep(0.34)
    client_name = partners.get('response')[0].get("first_name")
    return client_name


# Получить фамилию клиента/партнера
def get_person_surname(id):
    partner_response = requests.get(
        "https://api.vk.com/method/users.get",
        params={
            "access_token": token,
            "user_ids": id,
            "fields": "city,bdate,",
            "name_case": "Nom",
            "v": 5.124
        }
    )
    partners = partner_response.json()
    time.sleep(0.34)
    client_surname = partners.get('response')[0].get("last_name")
    return client_surname


# Получить возраст клиента/партнера
def get_person_age(id):
    partner_response = requests.get(
        "https://api.vk.com/method/users.get",
        params={
            "access_token": token,
            "user_ids": id,
            "fields": "city,bdate,",
            "name_case": "Nom",
            "v": 5.124
        }
    )
    partners = partner_response.json()
    time.sleep(0.34)
    client_age = partners.get('response')[0].get("bdate")
    return client_age


# Получить город клиента/партнера
def get_person_city(id):
    partner_response = requests.get(
        "https://api.vk.com/method/users.get",
        params={
            "access_token": token,
            "user_ids": id,
            "fields": "city,bdate,",
            "name_case": "Nom",
            "v": 5.124
        }
    )
    partners = partner_response.json()
    time.sleep(0.34)
    client_city = partners.get('response')[0].get("city").get("title")
    return client_city


# Получить количество лайков на топ 3 пролайканных фотографиях партнера
def get_photo_likes(id):
    likes = []
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
    if photo_json['response'].get('count') == 3:
        for elements in photo_json['response'].get('items'):
            like = elements.get('likes').get('count')
            likes.append(like)
        return likes
    elif photo_json['response'].get('count') >= 3:
        count_likes = []
        three_names = []
        for count in photo_json['response']['items']:
            count_likes.append(count.get('likes').get('count'))
        for photo in photo_json['response']['items']:
            name = 'photo' + str(photo.get('owner_id')) + '_' + str(photo.get('id'))
            three_names.append(name)
        tup = sorted(zip(count_likes, three_names), reverse=True)[:3]
        for like in tup:
            likes.append(like[0])
        return likes


# Создать словарь где key имя фотографии, value количество лайков
def make_dict_photo_and_likes(id):
    pholikes = dict(zip(get_photos_name(id), get_photo_likes(id)))
    return pholikes


# Отправка данных по клиенту в БД
def send_client_information_to_db():
    client_user = User(identity, get_person_name(identity), get_person_surname(identity), criterian[0], criterian[1],
                       get_person_city(identity), get_person_age(identity))
    session.add(client_user)
    return client_user


# Отправка данных по партнёру в БД
def send_patner_information_to_db(part_id, client):
    partner = Partner(part_id, get_person_name(part_id), get_person_surname(part_id), get_person_age(part_id),
                      client)
    session.add(partner)
    return partner


#  Отправка данных по фото партнёра в БД
def send_photo_information_to_db(part_id, link, likes):
    partner_photo = PhotoData(part_id, link, likes)
    session.add(partner_photo)


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
    write_message(identity, 'Здравствуйте, ' + get_person_name(identity) + '! ' +
                  'Вы хотите найти себе пару?', random.randint(-2147483648, 2147483647))
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            message_text = event.text.lower()
            print_information_about_message(message_text)
            if message_text == 'да':
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


# Отправка сразу 3 фотографий в одном письме чат бота
def cycle_sending_three_photos(vk_iden, choice):
    photo_name = get_photos_name(vk_iden)
    if photo_name:
        three = ''
        for photo in photo_name:
            three += photo + ','
        ready_three = three[:-1]
        send_photo(identity, 'https://vk.com/id' + str(vk_iden), attachment=ready_three)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                message_text = event.text.lower()
                if message_text == 'да':
                    if event.from_user:
                        write_message(identity, 'https://vk.com/id' + str(vk_iden) + congratulations,
                                      random.randint(-2147483648, 2147483647))
                        choice = not choice
                        return choice
                elif message_text == 'нет':
                    if event.from_user:
                        write_message(identity, do_not_worry, random.randint(-2147483648, 2147483647))
                        break


# Check existence of client or get him/her for next step of code
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        send_client_information_to_db()


criterian = []
choice_is_done = False
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
            write_message(identity, wait, random.randint(-2147483648, 2147483647))
            get_or_create(session, User, vk_id=identity)
            session.commit()
            all_partners = search_for_partner()
            truely_partners = clean_id_with_less_photos(all_partners)
            write_message(identity, check, random.randint(-2147483648, 2147483647))
            for id in truely_partners:
                choice_is_done = cycle_sending_three_photos(id, choice_is_done)
                print('Фото отправлены')
                if choice_is_done == True:
                    for user in session.query(User).filter_by(vk_id=identity):
                        send_patner_information_to_db(id, user.id)
                        session.commit()
                    for partner in session.query(Partner).filter_by(vk_id=id):
                        for name, like in make_dict_photo_and_likes(id).items():
                            send_photo_information_to_db(partner.id, name, like)
                            session.commit()
                    print('Поиск завершен!')
                    write_message(identity, advice_for_continue_search, random.randint(-2147483648, 2147483647))
