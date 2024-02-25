"""
Файл, в котором показан процесс получения статистики
"""

import vk_api
import urllib3
from math import ceil
from datetime import datetime

from dotenv import dotenv_values

secrets = dotenv_values(".env")
"""Секреты"""

vk = vk_api.VkApi(
    token=secrets['VK_TOKEN'])
"""Модуль ВК"""

id_chat = int(secrets['CHAT_ID'])
"""id чата"""

SHOULD_DOWNLOAD = False
"""Должна ли проводиться загрузка фото/стикеров"""


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

    result_image = urllib3.request('GET', url)
    """Полученное изображение"""
    with open(f'content/visual/images/{file_name}', 'wb') as image:
        image.write(result_image.data)


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
    result_sticker = urllib3.request('GET', f"https://vk.com/sticker/1-{id_sticker}-512b")
    """Полученный стикер"""
    with open(f'content/visual/stickers/{id_sticker}.png', 'wb') as f:
        f.write(result_sticker.data)


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
    # Требуется добавлять 2e9 по документации vk api
    peer_id += 2e9

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

    :return: ФИО в формате: Имя + " " + Фамилия
    :rtype: str

    """
    for profile in full_response['profiles']:
        if profile['id'] == user_id:
            return profile['first_name'] + ' ' + profile['last_name']
    # Если аккаунт пользователя удалён
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


length_chat = get_chat(count=1)['count']

for times_add in range(int(ceil(length_chat / 200))):
    delta = 200 * times_add
    """Отступ от первого сообщения"""
    response = get_chat(count=min(200, length_chat - delta), offset=delta)
    """count сообщений после delta"""
    for item in response['items']:
        # Проверка на действие
        if item.get('action'):
            continue

        date = get_date(item['date'])
        """Дата публикации сообщения"""
        username = get_fullname(item['from_id'], response)
        """ИФ пользователя"""

        # Загрузка доп данных
        if SHOULD_DOWNLOAD and item.get('attachments'):
            type_item = item['attachments'][0]['type']
            if type_item == 'photo':
                download_image(item['attachments'][0]['photo']['sizes'][-1]['url'])
            elif type_item == 'sticker':
                download_sticker(item['attachments'][0]['sticker']['sticker_id'])
                continue

        text_msg = item['text']
        """Текст сообщения"""

        # Если есть прикреплённые материалы
        if item.get('attachments'):

            # Если доп файл без подписи
            if text_msg == "":
                print(f"{date} — — {username} /—/ *Доп контент без подписи*")

            # Обычный случай
            else:
                match item['attachments'][0]['type']:
                    case 'sticker':
                        print(f"{date} — — {username} /—/ *стикер*")
                    case 'audio':
                        print(f"{date} — — {username} — {text_msg} /—/ *аудио*")
                    case 'doc':
                        print(f"{date} — — {username} — {text_msg} /—/ *документ/гифка*")
                    case 'video':
                        print(f"{date} — — {username} — {text_msg} /—/ *видео*")
                    case 'photo':
                        print(f"{date} — — {username} — {text_msg} /—/ *фото*")
                    case _:
                        print(f"{date} — — {username} — {text_msg} /—/ *нераспознанный доп контент*")
            continue

        # Если есть реакции
        if item.get('reactions'):
            print(
                f"{date} — — {username} — {text_msg} — {item['reactions']}")
            continue

        # Обычный случай
        print(f"{date} — — {username} — {text_msg}")
