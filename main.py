from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import vk
import random
from requests import *

token = "374eeed4f9510e8e6c2e5fbfbaab5f93c8068af27a245c2f729583018f34d608e7d740e2d349cf2d28997"
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)

session_api = vk_session.get_api()

def analize_message(event):
    words = event.text.split()
    path = "\\" + words[1] + "\\" + words[3] + ".jpg"
    print(path)

while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if not event.from_me:
                print(event.text)
                analize_message(event)
                if event.text == "семинар 1 задача 1":
                    vk_session.method("messages.send", {'user_id': event.user_id,
                                                        'message': event.text,
                                                        'random_id': 0, "attachment": ["photo-195223878_457239018"]})