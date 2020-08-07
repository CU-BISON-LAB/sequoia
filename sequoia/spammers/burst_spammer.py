# burst_spammer.py
# Invokes a batch of HTTP lambda functions at once.
from urllib.parse  import urlparse
import http.client, sys
from threading import Thread
import requests 
import queue
import time

# Number of invocations to run at once
concurrent = 1

# URL for the lambda function that should be invoked
url = "https://lambda1.com"

# Entry point of each worker thread.
# Pulls URLs off of the work queue to invoke HTTP requests for each one.
# Usually, each of these workers will only end up invoking one request.
def doWork(q, id):
    while True:
        url = q.get()
        status, url = getStatus(url, id)
        print (status, url.decode("utf-8"))
        q.task_done()

# Do an HTTP POST to the provided URL, passing parameters as needed
def getStatus(url, id):
    PARAMS = {'port':10000, 'ip':'127.0.0.1','id': str({id}), 'name':'functionSide'}
    res = requests.post(url = url, json = PARAMS, timeout=300)
    return res, res.content

# Work queue to track URLS we want to invoke
q = queue.Queue(concurrent * 2)
# Create a worker thread for each function we want to invoke
for i in range(concurrent):
    t = Thread(target=doWork, args=(q,i))
    t.daemon = True
    t.start()
try:
    for i in range(concurrent):
        q.put(url.strip())
    q.join()
except KeyboardInterrupt:
    sys.exit(1)
