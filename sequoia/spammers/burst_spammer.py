# burst_spammer.py
# Invokes a batch of HTTP lambda functions at once.
import sys
from threading import Thread
import requests 
import queue

# Number of invocations to run at once
burst_size = 1

# URL for the lambda function that should be invoked
url = "https://lambda1.com"

# Work queue to track URLS we want to invoke
work_queue = queue.Queue(burst_size * 2)

# Entry point of each worker thread.
# Pulls URLs off of the work queue to invoke HTTP requests for each one.
# Usually, each of these workers will only end up invoking one request.
def worker_thread(work_queue, uid):
    while True:
        url = work_queue.get()
        PARAMS = {'port':10000, 'ip':'127.0.0.1','id': str({uid}), 'name':'functionSide'}
        response = requests.post(url = url, json = PARAMS, timeout=300)
        print (response, response.content.decode("utf-8"))
        work_queue.task_done()

# Create a worker thread for each function we want to invoke
for i in range(burst_size):
    t = Thread(target=worker_thread, args=(work_queue,i))
    t.daemon = True
    t.start()

try:
    # Add each URL to the work queue to be consumed by the worker threads
    for i in range(burst_size):
        work_queue.put(url.strip())
    # Wait for all URLs to be consumed
    work_queue.join()
except KeyboardInterrupt:
    sys.exit(1)
