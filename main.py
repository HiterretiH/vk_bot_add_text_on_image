import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import requests
import image
from os import remove
import config


def get_name(id):
    info = vk.method('users.get', {'user_ids': id, 'name_case': 'nom'})
    info = info[0]
    return info['first_name'] + ' ' + info['last_name']


def send_image(path, user_id):
    a = vk.method('photos.getMessagesUploadServer')
    b = requests.post(a['upload_url'], files={'photo': open(path, 'rb')}).json()
    c = vk.method('photos.saveMessagesPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[0]
    d = 'photo{}_{}'.format(c['owner_id'], c['id'])

    vk.method('messages.send', {'user_id': user_id, 'attachment': d, 'random_id': get_random_id()})


def save_image(url, path='1.jpg'):
    a = requests.get(url).content
    f = open(path, 'wb')
    f.write(a)
    f.close()


vk = vk_api.VkApi(token=config.token)
longpoll = VkLongPoll(vk)

prev_id = 0
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me and event.message_id != prev_id:
            id_from = event.user_id
            if event.attachments and event.attachments['attach1_type'] == 'photo':
                a = vk.method('messages.getById', {'message_ids': event.message_id})
                print(f"""*Новое сообщение*
    Автор: {get_name(id_from)}
    Текст: {a['items'][0]['text']}
    Картинка: {a['items'][0]['attachments'][0]['photo']['sizes'][-1]['url']}\n""")
                text = a['items'][0]['text']
                url = a['items'][0]['attachments'][0]['photo']['sizes'][-1]['url']
                save_image(url)
                image.drawTextOnImage("1.jpg", text)
                send_image("done.jpg", id_from)
                remove("1.jpg")
                remove("done.jpg")
        prev_id = event.message_id
