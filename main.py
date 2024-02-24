from math import ceil

import vk_api
import csv
from datetime import datetime

from dotenv import dotenv_values

secrets = dotenv_values(".env")

vk = vk_api.VkApi(
    token=secrets['VK_TOKEN'])

id_chat = int(secrets['CHAT_ID'])


def get_chat(peer_id: int = id_chat + 2e9, count: int = 200, offset: int = 0) -> dict:
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
    return vk.method('messages.getHistory', {'peer_id': peer_id, 'count': count, 'offset': offset, 'rev': 1})


def get_names(chat_id: int = id_chat) -> dict:
    """

    Определение активных пользователей чата.

    Не определяет тех, кого удалили из чата.

    :param chat_id: id чата
    :type chat_id: int

    :return: Словарь с активными пользователями и их именами
    :rtype: dict

    """
    return vk.method('messages.getChat', {'chat_id': chat_id, 'fields': 'nickname'})


chat_userList = get_names()

user_list = {657900781: "DEAD1",
             303277718: "DEAD2",
             666136998: "Ilya Ghost",
             352169415: "Денис Севостьянов",
             267228976: "Александр Пушкарёв",
             529577677: "Максим Карманов",
             386198975: "Дмитрий Вегера",
             716192349: "Платон Иннокентьев",
             363974375: "Лёша Шафиков",
             744205905: "Алина Бондарева",
             256875938: "Евгений Мороз",
             354517433: "Алиса Матвеева",
             351280296: "Алиса Ильяхова",
             307446473: "Данил Ходос",
             394551912: "Алеусандр Меок",
             743621692: "Отгонцэцэг Бекболот",
             748572841: "Ab Chileshe",
             194841441: "Александр Ковш",
             328395011: "Александр Каменев",
             679024952: "Цзэхэн Цзун",
             85283476: "Эрсан Егоров",
             585367474: "Юрий Чернов",
             798986290: "Анастасия Протопопова",
             331092169: "Лёша Олегич",
             238781272: "Ярослав Прилипко",
             603817821: "Александра Корчевец",
             426574767: "Владислав Коняхин",
             386503702: "Егор Кузнецов",
             713935255: "Сергей Глущенко",
             410032691: "Артем Громыко",
             436770477: "Михаил Иванович",
             140356491: "Елизавета Исаева",
             320740678: "Андрей Красулин",
             443123379: "Аля Знаток",
             551132500: "Данил Крисько",
             320487643: "Марк Иванников",
             515310284: "Алексей Шелопаев",
             392886905: "Мишель Манько",
             532037098: "Настя Протопопова",
             334533103: "Лия Удовенко",
             554777162: "Даниил Плешанов",
             292489019: "Альбина Романенко",
             478112411: "Михаил Скуратов",
             195877005: "Виталий Луков",
             304937647: "Вероника Литвинова",
             369406825: "Олег Либих",
             265814146: "Андрей Корепанов",
             245482145: "Данил Башкайкин",
             305187037: "Максим Завязочников",
             351682559: "Никита Токарев",
             323307169: "Стас Бысь",
             378808075: "Алексей Сидоров",
             205170325: "Дарья Белоусова",
             388574277: "Настя Большакова",
             265311555: "Дмитрий Григорьев",
             417852815: "Вячеслав Григорьев",
             536025091: "Владислав Слободской",
             410924786: "Сергей Смирнов",
             365317881: "Polina Ling",
             406717867: "Дмитрий Садко",
             224395190: "Егор Волков",
             275396846: "Вова Немец",
             320332835: "Николай Миневич",
             237916242: "Денис Эм",
             403912742: "Арина Ажитова",
             750922944: "Бек Нуриллоев",
             660365788: "Катя Курбатова",
             778348772: "Степан Ражев",
             307278155: "Екатерина Крушинина",
             224258182: "Семён Аладин"}
"Список удалённых пользователей из CHAT_ID"

for user in chat_userList['users']:
    user_list[user['id']] = user['first_name'] + " " + user['last_name']

response = get_chat(count=1)
length_chat = response['count']

print(int(ceil(length_chat / 200)))

for times_add in range(877, int(ceil(length_chat / 200))):
    print(times_add)
    delta = 200 * times_add
    response = get_chat(count=min(200, length_chat - delta), offset=delta)
    for item in response['items']:

        if item.get('action'):
            continue
        if item.get('attachments') and item['attachments'][0]['type'] == 'sticker':
            print(
                f"{datetime.utcfromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S')} — — {user_list[item['from_id']]} /—/ *стикер*")
            continue
        if item.get('attachments') and item['attachments'][0]['type'] == 'doc':
            print(
                f"{datetime.utcfromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S')} — — {user_list[item['from_id']]} /—/ *документ/гифка*")
            continue
        if item.get('attachments') and item['attachments'][0]['type'] == 'photo' and item['text'] == "":
            print(
                f"{datetime.utcfromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S')} — — {user_list[item['from_id']]} /—/ *фото без подписи*")
            continue
        if item.get('reactions'):
            print('РЕАКЦИЯ!')
            print(
                f"{datetime.utcfromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S')} — — {user_list[item['from_id']]} — {item['text']} — {item['reactions']}")
            print('РЕАКЦИЯ!')
            continue
        print(
            f"{datetime.utcfromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S')} — — {user_list[item['from_id']]} — {item['text']}")
