from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import vk
import time
from pathlib import Path
import requests
import json


token = "374eeed4f9510e8e6c2e5fbfbaab5f93c8068af27a245c2f729583018f34d608e7d740e2d349cf2d28997"



vk_session = vk_api.VkApi(token=token)
vk_session1 = vk_api.VkApi('79611019237', 'fdf42fdf42')
vk_session1.auth()

longpoll = VkLongPoll(vk_session)
flag = 0
seminar = 0
task = 0

# lol = json()

with open("all_tasks.json") as f:
    all_tasks = json.load(f)

def write_in_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

affirmative = ["да", "верно", "правильно", "ес", "yes", "lf"]

def analize_message(event, all_tasks):
    if len(event.text.split()) == 4 or len(event.text.split()) == 2:
        words = event.text.split()
    else:
        vk_session.method("messages.send", {'user_id': event.user_id,
                                            'message': "Запрос не соответствует формату.\nВведите Семинар _ задача _ или просто 2 цифры",
                                            'random_id': 0})
        return (0, 0)
    if len(event.text.split()) == 4:
        try:
            int(words[1])
            int(words[3])
            if int(words[1]) > 10 or int(words[1]) < 1:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Cеминара " + str(words[1]) + " пока нет",
                                                    'random_id': 0})
                return (0, 0)
            if int(words[3]) > all_tasks['length'][words[1]] or int(words[3]) < 1:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "В семинаре " + str(words[1]) +
                                                           " нет задачи с номером " + str(words[3]) + "!",
                                                'random_id': 0})
                return (0, 0)
            return (words[1], words[3])
        except:
            vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "Введите числовое значение семинара и задачи по формату\nСеминар _ задача _ или просто 2 цифры",
                                                'random_id': 0})
    elif len(event.text.split()) == 2:
        try:
            int(words[0])
            int(words[1])
            if int(words[0]) > 10 or int(words[0]) < 1:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Cеминара " + str(words[0]) + " пока нет",
                                                    'random_id': 0})
                return (0, 0)
            if int(words[1]) > all_tasks['length'][words[0]] or int(words[1]) < 1:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "В семинаре " + str(words[0]) +
                                                           " нет задачи с номером " + str(words[1]) + "!",
                                                'random_id': 0})
                return (0, 0)
            return (words[0], words[1])
        except:
            vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "Введите числовое значение семинара и задачи по формату\nСеминар _ задача _ или просто 2 цифры",
                                                'random_id': 0})
    return (0, 0)

def get_photo(seminar, task, all_tasks):
    try:
        if '.com' in all_tasks[seminar][task]:
            print("Here")
            print(seminar)
            print(task)
            vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "Решение задания находится по ссылке:\n" + all_tasks[seminar][task],
                                                'random_id': 0})
            return 1
    except:
        vk_session.method("messages.send", {'user_id': event.user_id,
                                            'message': "Задачу " + str(task) + " из семинара " + str(seminar) + " еще никто не выложил",
                                            'random_id': 0})
        time.sleep(0.7)
        vk_session.method("messages.send", {'user_id': event.user_id,
                                            'message': "Желаете ли вы добавить ее?",
                                            'random_id': 0})
        return 0


def remember_users(user_id):
    try:
        open("user_id", "r")
        if user_id not in open("user_id", "r").read():
            write_in_file(user_id, "user_id")
    except:
        write_in_file(user_id, "user_id")

def analize_request(event, seminar, task, all_tasks):
    if seminar == 0:
        return 0
    else:
        if "attach1" in event.attachments.keys():
            all_tasks[seminar][task] = vk_session.method("messages.getHistoryAttachments", {'peer_id': event.user_id,
                                                    "media_type": "photo"})['items'][0]['attachment']['photo']['sizes'][-1]['url']
            write_in_file(all_tasks, "all_tasks.json")
            vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "Спасибо, что добавили решение задачи " + str(task) + " из семинара " + str(seminar) + "!",
                                                'random_id': 0})
        else:
            if task in all_tasks[seminar].keys() and ".com" in all_tasks[seminar][task]:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Решение задачи находится по ссылке\n" + all_tasks[seminar][task],
                                                    'random_id': 0})
            else:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Решение задачи еще не выложили",
                                                    'random_id': 0})
        print(event.attachments)


while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            # remember_users(event.user_id)
            if not event.from_me:
                seminar, task = analize_message(event, all_tasks)
                analize_request(event, seminar, task, all_tasks)
                print("seminar = " + str(seminar))
                print("task = " + str(task))