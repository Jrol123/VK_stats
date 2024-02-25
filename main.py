from math import ceil

import urllib3

import vk_api
import csv
from datetime import datetime

from dotenv import dotenv_values

import urllib3

secrets = dotenv_values(".env")

vk = vk_api.VkApi(
    token=secrets['VK_TOKEN'])

id_chat = int(secrets['CHAT_ID'])


def download_image(url: str) -> None:
    """

    Функция загрузки изображения

    :param url: URL адрес картинки
    :type url: str

    :return: Сохраняет картинку в папку
        Каждая картинка появляется лишь 1 раз
    :rtype: None

    """
    file_name = (url.split("/")[-1]).split("?")[0]
    """Имя картинки"""

    res = urllib3.request('GET', url)
    with open(f'content/visual/images/{file_name}', 'wb') as f:
        f.write(res.data)


def download_sticker(id_sticker: int) -> None:
    """

    Функция загрузки стикера

    :param id_sticker: Номер стикера
    :type id_sticker: int

    :return: Сохраняет стикер в папку
        Каждый стикер появляется лишь 1 раз
        Стикеры сохраняются в формате .png в разрешении 512x512
    :rtype: None

    """
    res = urllib3.request('GET', f"https://vk.com/sticker/1-{id_sticker}-512b")
    with open(f'content/visual/stickers/{id_sticker}.png', 'wb') as f:
        f.write(res.data)


def get_chat(peer_id: int = id_chat, count: int = 200, offset: int = 0) -> dict:
    """

    Позволяет получить сообщения из чата.

    :param peer_id: id чата.
        Работает через peer
    :type peer_id: int
    :param count: Количество получаемых сообщений <= 200
    :type count: int
    :param offset: Сдвиг от начального сообщения
    :type offset: int

    :return: Словарь с сообщениями и их параметрами
    :rtype: dict

    """
    peer_id += 2e9
    # Требуется добавлять 2e9 по документации vk api

    return vk.method('messages.getHistory',
                     {'peer_id': peer_id,
                      'count': count,
                      'offset': offset,
                      'rev': 1,
                      'extended': True}
                     )


def get_fullname(user_id: int, full_response: dict) -> str:
    """

    Получение полного имени пользователя

    API ВКонтакте выдаёт набор профилей пользователей, писавших сообщения
    Производится перебор id профилей и подбор под user_id

    :param user_id: ID пользователя
    :param full_response: Расширенный набор сообщений

    :return: ФИО в формате Имя + " " + Фамилия
    :rtype: str

    """
    for profile in full_response['profiles']:
        if profile['id'] == user_id:
            return profile['first_name'] + ' ' + profile['last_name']
    return 'EMPTY_USER' + ' ' + str(user_id)


def get_date(utc_date: int) -> str:
    """

    Перевод даты из UTC формата в нормальный формат

    :param utc_date: Дата в формате utc
    :type utc_date: int

    :return: Дата в формате YYYY-MM-DD HH:MM:SS
    :rtype: str

    """
    return datetime.utcfromtimestamp(utc_date).strftime('%Y-%m-%d %H:%M:%S')


response = get_chat(count=1)
length_chat = response['count']

for times_add in range(int(ceil(length_chat / 200))):
    # print(times_add)
    delta = 200 * times_add
    response = get_chat(count=min(200, length_chat - delta), offset=delta)
    for item in response['items']:

        if item.get('action'):
            continue
        if item.get('attachments') and item['attachments'][0]['type'] == 'sticker':
            print(
                f"{get_date(item['date'])} — — {get_fullname(item['from_id'], response)} /—/ *стикер*")
            continue
        if item.get('attachments') and item['attachments'][0]['type'] == 'doc':
            print(
                f"{get_date(item['date'])} — — {get_fullname(item['from_id'], response)} /—/ *документ/гифка*")
            continue
        if item.get('attachments') and item['attachments'][0]['type'] == 'video':
            print(
                f"{get_date(item['date'])} — — {get_fullname(item['from_id'], response)} /—/ *видео*")
            continue
        if item.get('attachments') and item['attachments'][0]['type'] == 'photo' and item['text'] == "":
            print(
                f"{get_date(item['date'])} — — {get_fullname(item['from_id'], response)} /—/ *фото без подписи*")
            # Раскомментить, если нужно загружать фото:
            # dowload_img(item['attachments'][0]['photo']['sizes'][-1]['url'])
            continue
        if item.get('reactions'):
            print('РЕАКЦИЯ!')
            print(
                f"{get_date(item['date'])} — — {get_fullname(item['from_id'], response)} — {item['text']} — {item['reactions']}")
            print('РЕАКЦИЯ!')
            continue
        print(
            f"{get_date(item['date'])} — — {get_fullname(item['from_id'], response)} — {item['text']}")
