#! /usr/bin/python3
# -*- coding: utf-8 -*-

import vk_api.longpoll
import time
import json
from group_digits import group_digits

token = "***"

vk_session = vk_api.VkApi(token=token)
longpoll = vk_api.longpoll.VkLongPoll(vk_session)

with open("all_tasks.json") as f:
    all_tasks = json.load(f)

def write_in_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

def response(event, text): 
    """
    отмечает сообщение как прочитанное и отвечает с небольшой паузой для эстетичности
    
    """
    
    time.sleep(0.7)
    vk_session.method("messages.markAsRead", {"peer_id": event.user_id , "v": 5.103})
    time.sleep(0.7)
    vk_session.method("messages.send", {'user_id': event.user_id, 'message': text, 'random_id': 0})

def analize_message(event, all_tasks):
    """
    проверяет соответствие запроса формату и сообщает, если он выходит за границы, в случае ошибки возвращает (0, 0)
    в случае соответствия возвращает два числа - номер семинара и номер задачи
    
    """
    
    if len(event.text.split()) == 2:
        words = event.text.split()
    else:
        response(event, "Запрос не соответствует формату.\n🚀 Введите через пробел номер семинара и номер задачи из него (например, '2 5' выдаст решение пятой задачи из второго семинара)")
        return (0, 0)
    try:
        int(words[0])
        int(words[1])
        if int(words[0]) > 12 or int(words[0]) < 1:
            response(event, "Cеминара " + str(words[0]) + " пока нет")
            return (0, 0)
        if int(words[1]) > all_tasks['length'][words[0]] or int(words[1]) < 1:
            response(event,  "В семинаре " + str(words[0]) + " нет задачи с номером " + str(words[1]) + "!")
            return (0, 0)
        return (words[0], words[1])
    except:
        response(event, "Запрос не соответствует формату.\n🚀 Введите через пробел номер семинара и номер задачи из него (например, '2 5' выдаст решение пятой задачи из второго семинара)")
    return (0, 0)

def remember_users(user_id):
    """
    функция проверяет наличие пользователя, отправившего сообщение, в списке, если его нет - добавляет.
    основная задача - грамотно обработать приветствие только в том случае, если пользователь пишет первый раз.
    возвращает 0 в случае, если пользователь новый, и 1, если он уже был в списке.
    
    """
    
    with open('user_id', "r") as f:
        if str(user_id) not in f.read():
            x = 1
        else:
            x = 0
    if x == 1:
        with open('user_id', "a+") as file:
                file.write(str(user_id))
                file.write('\n')
                return 0
    else:
        return 1

def analize_request(event, seminar, task, all_tasks):
    """
    по сути сердце работы бота, здесь обрабатываются сообщения после того, как они прошли через первоначальную фильтрацию на соответствие формату.
    снчала выполняется проверка на то, что все вложения являются фотографиями, далее на наличие решения указанной задачи.
    затем формируется строка обращения к фотографии.
    далее 2 пути:
    1. если фото добавил модератор, то создатеся ключ задачи в нужном семинаре, которому сооотвествует другой словарь с ключами, которые служат для обращения
    к каждой фотографии.
    2. если фото добавил не модератор, то в цикле каждому модератору отправляется сообщение с вложениями, в то же время строка для обращения к фото удаляется.
    когда хотя бы 1 из модераторов подтвердит добавеление, строка будет добавена в all_tasks.json - эта функция реализована ниже
    
    """
    
    if seminar == 0:
        return 0
    else:
        if "attach1" in event.attachments.keys():
            for i in range(1, int(len(str(event.attachments.keys()).split())/2) + 1):
                if event.attachments['attach' + str(i) + "_type"] != "photo":
                    response(event, "Решением задачи может быть только фото")
                    return 0
            r = vk_session.method("messages.getById", {"message_ids": event.message_id})
            access_key = []
            if task in all_tasks[seminar].keys() and "0" in all_tasks[seminar][task].keys() and "photo" in all_tasks[seminar][task]['0']:
                response(event, "Задача " + str(task) + " из семинара " + str(seminar) + " уже решена")
                response(event, "Если вы хотите заменить существующее решение, напишите @saturnnm (Мне) в лс")
                return 0
            else:
                all_tasks[seminar][task] = {}
            for i in range(0, int(len(str(event.attachments.keys()).split())/2)):
                access_key.append(r['items'][0]['attachments'][i]['photo']['access_key'])
                string = "photo" + str(event.attachments["attach" + str(i+1)]) + "_" + str(access_key[i])
                all_tasks[seminar][task][str(i)] = string
            with open("moderators_ids", "r") as f:
                moderators = f.read()
                if str(event.user_id) in moderators:
                    write_in_file(all_tasks, "all_tasks.json")
                else:
                    attach = str(all_tasks[seminar][task]['0'])
                    for i in range(1, all_tasks[seminar][task].keys().__len__()):
                        attach += "," + str(all_tasks[seminar][task][str(i)])
                    for j in moderators.split('\n'):
                        vk_session.method("messages.send", {'user_id': int(j),
                                                            'message':  seminar + " " + task,
                                                            'random_id': 0,
                                                            'attachment': attach})
                    delete_image(event.text, all_tasks)
            user = vk_session.method("users.get", {"user_ids": event.user_id})
            response(event,  user[0]['first_name'] + ", спасибо, что добавили решение задачи " + str(task) + " из семинара " + str(seminar) + "!")
        else:
            if task in all_tasks[seminar].keys() and '0' in all_tasks[seminar][task].keys() and "photo" in all_tasks[seminar][task]['0']:
                attach = str(all_tasks[seminar][task]['0'])
                for i in range(1, all_tasks[seminar][task].keys().__len__()):
                    attach += "," + str(all_tasks[seminar][task][str(i)])
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Решение задачи " + task + " из семинара "+ seminar + ":",
                                                    'random_id': 0,
                                                    'attachment': attach})

            else:
                response(event, "Решение задачи еще не выложили 🐨")
            return 0

def ask_help(event):
    """
    просто выводит список правил, вызывается командой "хелп"
    
    """
    
    response(event, "Подсказака:\n\n" + "⚡ Чтобы получить решение задачи, введите через пробел номер семинара и номер задачи из него (например, '2 5' выведет решение пятой задачи из второго семинара)\n\n"
        + "⚡ Добавить свое решение можно прикрепив фото к сообщению с номером семинара и задачи.\n\n"
        + "❗ Команда 'все' выведет список всех добавленных задач.\n\n"
        + "⚡ Вызвать подсказку еще раз можно командой 'хелп'.\n\n"
        + "По другим вопросам пишите @saturnnm (Мне) 😉")

def delete_image(text, all_tasks):
    """
    функция для админки, вызывается специальной командой, в данном случае "<семинар> <задача> delete23012001"
    удаляет все ссылки на фотографии сотвествующие решению указанной задачи, а также ключ, соответствующий задаче
    
    """
    
    words = text.split()
    if words[1] in all_tasks[words[0]].keys():
        for i in list(all_tasks[words[0]][words[1]].keys()):
            del all_tasks[words[0]][words[1]][i]
        del all_tasks[words[0]][words[1]]
        write_in_file(all_tasks, "all_tasks.json")
    return all_tasks

def print_all_tasks(all_tasks, event):
    """
    выводит список всех решенных задач, с группировкой чисел идущих подряд, чтобы не захламлять экран
    
    """
    
    string = ""
    for seminar in all_tasks.keys():
        if seminar != "length":
            string += str(seminar) + ": "
            tasks_array = []
            for task in (all_tasks[seminar].keys()):
                tasks_array.append(int(task))
            tasks_array = sorted(tasks_array)
            string = string + ', '.join(group_digits(tasks_array)) + "\n"
    response(event, string)

def accept_photo(event):
    """
    функция, которая обеспечивает удобство жизни модераторам. в случае, если бот получает reply с любым текстом от модератора, то он добавляет вложения в all_tasks.json
    если reply получен от обычного пользователя, то ему предлагают изменить запрос и его действия нигде не учитываются.
    
    """
    
    with open("moderators_ids", "r") as f:
        if str(event.user_id) in f.read():
            r = vk_session.method("messages.getById", {"message_ids": event.message_id})
            words = r['items'][0]['reply_message']['text'].split()
            if words[1] in all_tasks[words[0]]:
                vk_session.method("messages.send", {'user_id': event.user_id,
                                                    'message': "Спасибо, уже добавлена",
                                                    'random_id': 0})
            else:
                boarder = len(r['items'][0]['reply_message']['attachments'])
                attach = []
                if words[1] not in all_tasks[words[0]].keys():
                    all_tasks[words[0]][words[1]] = {}
                    for i in range(0, boarder):
                        attach.append("photo" + str(r['items'][0]['reply_message']['attachments'][i]['photo']['owner_id']) + "_" + str(r['items'][0]['reply_message']['attachments'][i]['photo']['id']) + "_" + str(r['items'][0]['reply_message']['attachments'][i]['photo']['access_key']))
                        all_tasks[words[0]][words[1]][str(i)] = attach[i]
                    write_in_file(all_tasks, "all_tasks.json")
                    response(event, "Добавлено, спасибо!")
         else:
            response(event, "Введите 'хелп', чтобы увидеть подсказку.")
    
def main(all_tasks):
    """
    в main идет бесконечный цикл, в котором запущен метод longpoll.listen(), который "прослушивает" сообщения, которые приходят боту.
    каждая стпуень проверят куда отправить запрос, и перенаправляет полученные данные в нужную функцию.
    конструкция try ... except использована для того, чтобы
    во-первых, обойти ограничение, установленное методом longpoll.listen(). он запускает таймер и если никто не пишет в течение нескольких минут, то он выдает ошибку.
    во-вторых, предотвратить поломку бота в случае, если кто-то из пользователей введет запрос, который будет нечаественно обработан ботом и приведет к ошибке
    
    """
    
    x = 1
    try:
        while x == 1:
            for event in longpoll.listen():
                if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
                    if not event.from_me:
                        c = remember_users(event.user_id)
                        if event.text == "хелп" or c == 0:
                            if c == 0:
                                user = vk_session.method("users.get", {"user_ids": event.user_id})
                                response(event, "Привет, " + user[0]['first_name'] + "!")
                            ask_help(event)
                        elif event.text == "error":
                            print(lol)
                        elif event.text == "stop23012001":
                            x = 0
                            break
                        elif "reply" in event.attachments.keys():
                            accept_photo(event)
                        elif "delete23012001" in event.text:
                            all_tasks = delete_image(event.text, all_tasks)
                        elif event.text.lower() == "все":
                            print_all_tasks(all_tasks, event)
                        elif event.text.lower() == "спасибо":
                            response(event, "Пожалуйста)")
                        else:
                            seminar, task = analize_message(event, all_tasks)
                            analize_request(event, seminar, task, all_tasks)
    except Exception as e:
        print("Error occured.")
        print(e)
        main(all_tasks)

if __name__ == "__main__":
    main(all_tasks)
