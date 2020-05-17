import time

time_sent = time.time()
print(time_sent)
time.sleep(5)
time_sent1 = time.time()
print(time_sent)
print(time_sent1 - time_sent)
