from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import vk
import time
from pathlib import Path
import requests
import json


token = "374eeed4f9510e8e6c2e5fbfbaab5f93c8068af27a245c2f729583018f34d608e7d740e2d349cf2d28997"
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)
flag = 0
seminar = 0
task = 0

all_tasks = {'1': {}, '2': {}, '3': {}, '4': {}, '5': {}, '6': {}, '7': {}, '8': {}, '9': {}, '10': {},
             'length': {'1': 21, '2': 13, '3': 34, '4': 17, '5': 30, '6': 19, '7': 20, '8': 19, '9': 16, '10': 12}}
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
            if int(words[1]) > 10:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Cеминара " + str(words[1]) + " пока нет",
                                                    'random_id': 0})
                return (0, 0)
            if int(words[3]) > all_tasks['length'][words[1]]:
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
            if int(words[0]) > 10:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Cеминара " + str(words[0]) + " пока нет",
                                                    'random_id': 0})
                return (0, 0)
            if int(words[1]) > all_tasks['length'][words[0]]:
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
        if '-' in all_tasks[seminar][task]:
            print("Here")
            vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "",
                                                'random_id': 0,
                                                'attachment': "photo" + all_tasks[seminar][task]})
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

# def write_in_file(data, filename):
#     with open(filename, 'w') as file:
#         json.dump(data, file)

def ask_to_upload(event, seminar, task):
    if event.text in affirmative:
        vk_session.method("messages.send", {'user_id': event.user_id,
                                            'message': "Отправьте сообщение, прикрепив к ней фото с решением задачи",
                                            'random_id': 0})
        return 1
    else:
        vk_session.method("messages.send", {'user_id': event.user_id,
                                            'message': "Попросим других пользователей добавить ответ на задачу",
                                            'random_id': 0})
        print("fuu")
        # просит пользователей из списка прислать решение задачи
        return 0

x = 1

def write_in_file(data, filename):
    with open(filename, "w") as file:
        json.dump(data, filename)

def remember_users(user_id):
    try:
        open("user_id", "r")
        if user_id not in open("user_id", "r").read():
            write_in_file(user_id, "user_id")
    except:
        write_in_file(user_id, "user_id")


while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            # remember_users(event.user_id)
            if not event.from_me:
                if seminar == 0:
                    vk_session.method("messages.send", {'user_id': event.user_id,
                                                        'message': "1",
                                                        'random_id': 0,
                                                        'attachment': ['photo149640303_457243386']})

                    seminar, task = analize_message(event, all_tasks)
                    print("seminar = " + str(seminar))
                    print("task = " + str(task))
                if seminar != 0:
                    if x == 0:
                        if flag != 1 and ask_to_upload(event, seminar, task) == 0:
                            x = 1
                            seminar = 0
                        else:
                            if flag == 1:
                                all_tasks[seminar][task] = event.attachments['attach1']
                                print(event.attachments)
                                attach = "photo" + str(all_tasks[seminar][task])
                                print(attach)
                                vk_session.method("messages.send", {'user_id': event.user_id,
                                                                    'message': "1",
                                                                    'random_id': 11,
                                                                    'attachment': [str(attach)]})
                                print(all_tasks)
                                flag = 0
                                x = 1
                                seminar = 0
                            else:
                                flag= 1
                    else:
                        x = get_photo(seminar, task, all_tasks)