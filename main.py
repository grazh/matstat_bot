#! /usr/bin/python3
# -*- coding: utf-8 -*-

import vk_api.longpoll
import vk
import time
import json
import requests
import wget
import os

token = "374eeed4f9510e8e6c2e5fbfbaab5f93c8068af27a245c2f729583018f34d608e7d740e2d349cf2d28997"


vk_session = vk_api.VkApi(token=token)
vk_session1 = vk_api.VkApi("79611019237", "fdf42fdf42")
vk_session1.auth()
longpoll = vk_api.longpoll.VkLongPoll(vk_session)

with open("all_tasks.json") as f:
    all_tasks = json.load(f)
    print(type(all_tasks))
    print(type(all_tasks["6"]))

def write_in_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

affirmative = ["да", "Да", "lf"]

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

def remember_users(user_id):
    try:
        open("user_id", "r")
        if user_id not in open("user_id", "r").read().split():
            write_in_file(user_id.append("\n"), "user_id")
            return 0
        return 1
    except:
        write_in_file(user_id, "user_id")

def analize_request(event, seminar, task, all_tasks):
    if seminar == 0:
        return 0
    else:
        if "attach1" in event.attachments.keys():
            # all_tasks[seminar][task] =
            photo_url = vk_session.method("messages.getHistoryAttachments", {'peer_id': event.user_id,
                                                    "media_type": "photo"})['items'][0]['attachment']['photo']['sizes'][-1]['url']
            local_image_filename = wget.download(photo_url)
            r = vk_session1.method("photos.getUploadServer", {'album_id': 272202001,
                                                        'group_id': 195223878,
                                                        'v': 5.103})
            url = r['upload_url']
            with open(local_image_filename, "rb") as f:
                file = {"file1": f}
                ur = requests.post(url, files=file).json()
            photo = vk_session1.method("photos.save", {'album_id': 272202001,
                                                                        'group_id': 195223878,
                                                                       'server': ur['server'],
                                                                       'photos_list': ur['photos_list'],
                                                                       'hash': ur['hash']})
            print(photo)
            string = "photo" + str(photo[0]['owner_id']) + "_" + str(photo[0]['id'])
            all_tasks[seminar][task] = string
            write_in_file(all_tasks, "all_tasks.json")
            vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "Спасибо, что добавили решение задачи " + str(task) + " из семинара " + str(seminar) + "!",
                                                'random_id': 0})
            os.remove(local_image_filename)
        else:
            if task in all_tasks[seminar].keys() and "photo" in all_tasks[seminar][task]:
                print(all_tasks[seminar][task])
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Решение задачи " + task + " из семинара " + seminar + ":",
                                                    'random_id': 0,
                                                    'attachment': [all_tasks[seminar][task]]})
            else:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Решение задачи еще не выложили",
                                                    'random_id': 0})

def ask_help(event):
    vk_session.method("messages.send", {"user_id": event.user_id,
        "message": "Чтобы получить решение задачи введите\nСеминар _ задача _\nили просто две цифры, соответствующие номеру семинара и задачи.\n\n"
        + "Чтобы добавить свое решение, отправьте сообщение с номером семинара и задачи и прикрепите к нему фото с решением\n\n"
        + "Чтобы увидеть подсказку еще раз, напишите 'помощь'\n"
        + "По другим вопросам пишите @saturnnm (Мне)",
        "random_id": 0})

def delete_image(text, all_tasks):
    words = text.split()
    if words[2] in all_tasks[words[1]].keys():
        del all_tasks[words[1]][words[2]]
        write_in_file(all_tasks, "all_tasks.json")

def main(all_tasks, seminar):
    x = 1
    try:
        while x == 1:
            for event in longpoll.listen():
                if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
                    if not event.from_me:
                        if event.text == "помощь" or seminar == 'first':
                            if remember_users(event.user_id) == 0:
                                vk_session.method("messages.send", {"user_id": event.user_id,
                                                                    "message": "Приветствую тебя!",
                                                                    "random_id": 0})
                            ask_help(event)
                            seminar = 0
                        elif event.text == "stop23012001":
                            x = 0
                            break
                        elif "delete23012001" in event.text:
                            delete_image(event.text, all_tasks)
                        elif len(event.text.split()) == 2 or len(event.text.split()) == 4:
                            seminar, task = analize_message(event, all_tasks)
                            analize_request(event, seminar, task, all_tasks)
    except ZeroDivisionError:
        print("Error occured.")
        main(all_tasks, 0)

if __name__ == "__main__":
    main(all_tasks, "first")
