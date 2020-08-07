# continuous_spammer.py
# Continuously invokes HTTP lambda functions over a period of time.
from urllib.parse  import urlparse
import http.client, sys
from threading import Thread
import requests
import queue
import time
import random
import threading

# Number of functions to invoke each second
concurrent = 1000

# Number of iterations to run the spammer
no_of_iterations = 6

# Number of seconds between each iteration
seconds_between_iters = 15

# Entry point of each worker thread.
def doWork(url, id, chain):
    status, url = getStatus(url, id, chain)
    print(status, url)

# Do an HTTP POST to the provided URL, passing parameters as needed
def getStatus(url, id, chain):
    PARAMS = {"id": id}
    res = requests.get(url = url, params = PARAMS, timeout=300)
    return res, res.content

iid = 0
count = 0
# Perform one iteration
def iteration(iter):
    url1 = "lambda1.com"
    url2 = "lambda2.com"
    url3 = "lambda3.com"
    start = time.time()
    thread2Count = 0
    for i in range(concurrent):
        global iid
        global count
        t1 = Thread(target=doWork, args=(url1,iid,'chain1'))
        t1.start()
        if iter > 500:
          if thread2Count < 23:
            t2 = Thread(target=doWork, args=(url1,iid, 'chain2'))
            thread2Count = thread2Count + 1
        t3 = Thread(target=doWork, args=(url1,iid, 'chain3'))
        iid = iid + 1
    elapsed = time.time() - start
    if seconds_between_iters-elapsed>0:
        time.sleep(seconds_between_iters-elapsed)

# Perform all iterations
for i in range(no_of_iterations):
    print('iteration no:', i, 'with concurrent', concurrent)
    iteration(i)
