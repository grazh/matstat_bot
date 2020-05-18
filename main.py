#! /usr/bin/python3
# -*- coding: utf-8 -*-

import vk_api.longpoll
import time
import json

def pause():
    return 0.5
token = "374eeed4f9510e8e6c2e5fbfbaab5f93c8068af27a245c2f729583018f34d608e7d740e2d349cf2d28997"


vk_session = vk_api.VkApi(token=token)
longpoll = vk_api.longpoll.VkLongPoll(vk_session)

with open("all_tasks.json") as f:
    all_tasks = json.load(f)

def write_in_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

affirmative = ["да", "Да", "lf"]

def mark_as_read(event):
    time.sleep(0.7)
    vk_session.method("messages.markAsRead", {"peer_id": event.user_id , "v": 5.103})
    time.sleep(0.7)

def analize_message(event, all_tasks):
    if len(event.text.split()) == 4 or len(event.text.split()) == 2:
        words = event.text.split()
    else:
        mark_as_read(event)
        vk_session.method("messages.send", {'user_id': event.user_id,
                                            'message': "Запрос не соответствует формату.\nВведите Семинар _ задача _ или просто 2 цифры",
                                            'random_id': 0})
        return (0, 0)
    if len(event.text.split()) == 4:
        try:
            int(words[1])
            int(words[3])
            if int(words[1]) > 10 or int(words[1]) < 1:
                mark_as_read(event)
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Cеминара " + str(words[1]) + " пока нет",
                                                    'random_id': 0})
                return (0, 0)
            if int(words[3]) > all_tasks['length'][words[1]] or int(words[3]) < 1:
                mark_as_read(event)
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "В семинаре " + str(words[1]) +
                                                           " нет задачи с номером " + str(words[3]) + "!",
                                                'random_id': 0})
                return (0, 0)
            return (words[1], words[3])
        except:
            mark_as_read(event)
            vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "Введите числовое значение семинара и задачи по формату\nСеминар _ задача _ или просто 2 цифры",
                                                'random_id': 0})
    elif len(event.text.split()) == 2:
        try:
            int(words[0])
            int(words[1])
            if int(words[0]) > 10 or int(words[0]) < 1:
                mark_as_read(event)
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Cеминара " + str(words[0]) + " пока нет",
                                                    'random_id': 0})
                return (0, 0)
            if int(words[1]) > all_tasks['length'][words[0]] or int(words[1]) < 1:
                mark_as_read(event)
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "В семинаре " + str(words[0]) +
                                                           " нет задачи с номером " + str(words[1]) + "!",
                                                'random_id': 0})
                return (0, 0)
            return (words[0], words[1])
        except:
            mark_as_read(event)
            vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "Введите числовое значение семинара и задачи по формату\nСеминар _ задача _ или просто 2 цифры",
                                                'random_id': 0})
    return (0, 0)

def remember_users(user_id):
    with open('user_id', "r") as f:
        if str(user_id) not in f.read():
            with open('user_id', "w") as file:
                file.write(str(user_id))
                file.write('\n')
                return 0

def analize_request(event, seminar, task, all_tasks):
    if seminar == 0:
        return 0
    else:
        print(event.attachments)
        if "attach1" in event.attachments.keys():
            for i in range(1, int(len(str(event.attachments.keys()).split())/2) + 1):
                if event.attachments['attach' + str(i) + "_type"] != "doc" and event.attachments['attach' + str(i) + "_type"] != "photo":
                    vk_session.method("messages.send", {'user_id': event.user_id,
                                                        'message': "Решением задачи может быть только фото или документ",
                                                        'random_id': 0})
                    return 0
            if "photo" in all_tasks[seminar][task]['0']:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Задача " + str(task) + " из семинара " + str(seminar) + " уже решена",
                                                    'random_id': 0})
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Наберите: " + str(seminar) + " " + str(task),
                                                    'random_id': 0})
                return 0
            r = vk_session.method("messages.getById", {"message_ids": event.message_id})
            access_key = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            all_tasks[seminar][task] = {}
            for i in range(0, int(len(str(event.attachments.keys()).split())/2)):
                access_key[i] = r['items'][0]['attachments'][i]['photo']['access_key']
                string = "photo" + str(event.attachments["attach" + str(i+1)]) + "_" + str(access_key[i])
                all_tasks[seminar][task][i] = string
            write_in_file(all_tasks, "all_tasks.json")
            mark_as_read(event)
            vk_session.method("messages.send", {'user_id': event.user_id,
                                                'message': "Спасибо, что добавили решение задачи " + str(task) + " из семинара " + str(seminar) + "!",
                                                'random_id': 0})
        else:
            if task in all_tasks[seminar].keys() and "photo" in all_tasks[seminar][task]['0']:
                mark_as_read(event)
                attach = str(all_tasks[seminar][task]['0'])
                for i in range(1, all_tasks[seminar][task].keys().__len__()):
                    attach += "," + str(all_tasks[seminar][task][str(i)])
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Решение задачи " + task + " из семинара " + seminar + ":",
                                                    'random_id': 0,
                                                    'attachment': attach})
            else:
                mark_as_read(event)
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Решение задачи еще не выложили",
                                                    'random_id': 0})
            return 0

def ask_help(event):
    mark_as_read(event)
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

def print_all_tasks(all_tasks, event):
    string = ""
    for seminar in all_tasks.keys():
        if seminar != "length":
            string += str(seminar) + ": "
            tasks_array = []
            for task in (all_tasks[seminar].keys()):
                tasks_array.append(int(task))
            for task1 in sorted(tasks_array):
                string += str(task1) + ", "
            string += "\n"
    vk_session.method("messages.send", {"user_id": event.user_id, "message": string, "random_id": 0})

def main(all_tasks, seminar):
    x = 1
    previous_url = 0
    try:
        while x == 1:
            for event in longpoll.listen():
                if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
                    if not event.from_me:
                        if event.text == "помощь" or seminar == 'first':
                            if remember_users(event.user_id) == 0:
                                mark_as_read(event)
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
                        elif event.text == "Все" or event.text == "все":
                            print_all_tasks(all_tasks, event)
                        elif len(event.text.split()) == 2 or len(event.text.split()) == 4:
                            seminar, task = analize_message(event, all_tasks)
                            analize_request(event, seminar, task, all_tasks)
    except:
        print("Error occured.")
        main(all_tasks, 0)

if __name__ == "__main__":
    main(all_tasks, "first")