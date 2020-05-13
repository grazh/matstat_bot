from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from openpyxl import Workbook
from openpyxl import load_workbook
import time


token = "374eeed4f9510e8e6c2e5fbfbaab5f93c8068af27a245c2f729583018f34d608e7d740e2d349cf2d28997"
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)

while True:
    for event in longpoll.listen()