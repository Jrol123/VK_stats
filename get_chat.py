"""
Файл, в котором показан процесс получения статистики
"""

import vk_api
import urllib3
import pandas as pd
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
            # Если аккаунт пользователя удалён
            if profile['first_name'] == 'DELETED':
                return 'EMPTY_USER' + ' ' + str(user_id)
            return profile['first_name'] + ' ' + profile['last_name']


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
"""Количество сообщений в чате"""
# print(int(ceil(length_chat / 200)))

msg_mass = []
"""Массив сообщений"""

count_dead_msg = 0
"""Количество удалённых сообщений, на которые был дан ответ"""

print("id — date — isAction — username — text — attachments — reactions — response")

start_time = datetime.now()
"""Время начала получения статистики"""
for times_add in range(870, int(ceil(length_chat / 200))):

    print(times_add)
    delta = 200 * times_add
    """Отступ от первого сообщения"""
    messages = get_chat(count=min(200, length_chat - delta), offset=delta)
    """count сообщений после delta"""

    for item_data in messages['items']:
        attachments = {'type': None,
                       'value': []
                       # Содержит в себе название файла
                       }
        """Прикреплённые доп. материалы"""
        if item_data.get('attachments'):

            for attachment in item_data['attachments']:
                if attachment['type'] == 'photo':
                    attachments['type'] = 'photo'
                    attachments['value'].append(
                        (((attachment['photo']['sizes'][-1]['url']).split("/")[-1]).split("?"))[0]
                    )
                elif attachment['type'] == 'sticker':
                    attachments['type'] = 'sticker'
                    attachments['value'].append(str(attachment['sticker']['sticker_id']) + ".png")
            if attachments['type'] is None:
                attachments = {}
        else:
            attachments = {}

        reactions = {}
        """Реакции"""
        if item_data.get('reactions'):
            # Почему-то не всегда показывает тех, кто ставил реакции
            # #1
            for reaction in item_data['reactions']:
                user_list = [reaction['count']]
                for user in reaction['user_ids']:
                    user_list.append(get_fullname(user, messages))
                reactions[reaction['reaction_id']] = user_list

        response = {'id': None,
                    'date': None,
                    'user': {'id': None,
                             'username': None,
                             },
                    'text': None,
                    'attachments': {'type': None,
                                    'value': []
                                    # Содержит в себе название файла
                                    }
                    }
        """Ответ на сообщение"""
        if item_data.get('reply_message'):
            reply = item_data['reply_message']
            if reply.get('conversation_message_id'):
                response['id'] = reply['conversation_message_id']
            if not reply.get('conversation_message_id') or response['id'] == 0:
                response['id'] = f'f{count_dead_msg}'
                count_dead_msg += 1
            response['date'] = get_date(reply['date'])
            response['user']['id'] = reply['from_id']
            response['user']['username'] = get_fullname(reply['from_id'], messages)
            response['text'] = reply['text']

            for attachment in reply['attachments']:
                if attachment['type'] == 'photo':
                    response['attachments']['type'] = 'photo'
                    response['attachments']['value'].append(
                        (((attachment['photo']['sizes'][-1]['url']).split("/")[-1]).split("?"))[0]
                    )
                elif attachment['type'] == 'sticker':
                    response['attachments']['type'] = 'sticker'
                    response['attachments']['value'].append(str(attachment['sticker']['sticker_id']) + ".png")
            if response['attachments']['type'] is None:
                response['attachments'] = {}
        else:
            response = {}

        item = {'id': item_data['id'],
                'date': get_date(item_data['date']),
                'isAction': item_data.get('action'),
                'user': {'id': item_data['from_id'],
                         'username': get_fullname(item_data['from_id'], messages)
                         },
                'text': item_data['text'],
                'attachments': attachments,
                'reactions': reactions,
                'response': response
                }
        """Сообщение"""

        msg_mass.append(item)

        # Загрузка доп данных
        if SHOULD_DOWNLOAD and item_data.get('attachments'):
            for attachment in item_data['attachments']:
                if attachment['type'] == 'photo':
                    download_image(attachment['photo']['sizes'][-1]['url'])
                elif attachment['type'] == 'sticker':
                    download_sticker(attachment['sticker']['sticker_id'])

end_time = datetime.now()
"""Время завершения программы получения статистики"""
print(end_time - start_time)

df = pd.DataFrame(msg_mass)
