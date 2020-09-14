# continuous_spammer.py
# Periodically invokes bursts of HTTP lambda functions over a period of time.
from threading import Thread
import requests
import time

# Serverless functions
url1 = "lambda1.com"
url2 = "lambda2.com"

# Number of functions to invoke in each iteration
burst_size = 1000

# Number of iterations to run the spammer
no_of_iterations = 6

# Number of seconds between each iteration
seconds_between_iters = 15

# Iteration number to start invoking url2
start_iteration_url2 = 501

# Entry point of each worker thread.
# Invoke a serverless function at the specified url.
def invoke_function(function_url, uid):
    PARAMS = {"id": uid}
    response = requests.get(url = function_url, params = PARAMS, timeout=300)
    print(response, response.content)

uid = 0
# Perform one iteration, then sleep for seconds_between_iters
def do_burst(iter_number):
    for i in range(burst_size):
        global uid
        t1 = Thread(target=invoke_function, args=(url1,uid))
        t1.start()
        if iter_number >= start_iteration_url2:
            t2 = Thread(target=invoke_function, args=(url2,uid))
            t2.start()
        uid = uid + 1

# Perform all iterations and sleep between each of them
for i in range(no_of_iterations):
    print('iteration no:', i, 'with burst_size', burst_size)
    start = time.time()
    do_burst(i)
    elapsed = time.time() - start
    if seconds_between_iters > elapsed:
        time.sleep(seconds_between_iters-elapsed)
