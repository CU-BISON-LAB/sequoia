# sequoia.py
# Function wrapper for instrumenting serverless functions with logging for the
# Sequoia serverless framework
from datetime import datetime
from functools import partial
from socket import socket, AF_INET, SOCK_STREAM
from time import time

# Return a timestamp to include in log data
def _get_timestamp():
    raw_ts = time()
    st2 = datetime.fromtimestamp(raw_ts).strftime('%f')
    st = str(raw_ts).split('.')
    return st[0] + "." + st2

# Attempt to connect to the Logging Framework to send an IP address
def _send_message(name, status, time, uid, ip, port):
    sock = socket(AF_INET, SOCK_STREAM)
    server_address = (ip, port)
    print("Connecting to {}:{}".format(ip, port))
    sock.connect(server_address)
    try:
        message = name+"-"+status+"-"+time+"-"+str(uid)+"\n"
        sock.sendall(message.encode())
    finally:
        sock.close()

# Actual wrapper for the serverless function
# If porting to something other than AWS, replace event and context with the
# parameters passed to your serverless function's entrypoint.
def _function_wrapper(ip, port, lambda_handler, event, context):
    name = event.get("name", "lambda")
    uid = event["id"]
    _send_message(name, "start", _get_timestamp(), uid, ip, port)
    output = lambda_handler(event, context)
    _send_message(name, "end", _get_timestamp(), uid, ip, port)
    return output

## The rest of the file from here is function decorator implementation

# Pulls the IP and port from the arguments passed to the serverless function at
# runtime. If using a platform other than AWS, this must be updated to use the
# new platform's method of reading serverless function parameters.
def _dynamic_function(lambda_handler, event, context):
    ip = event["ip"]
    port = int(event.get("port", 10000))
    return _function_wrapper(ip, port, lambda_handler, event, context)

# sequoia.function decorator
# Can be called in two ways:
#   @sequoia.function
#   def myfunc(event, context):
#     ...
# 
#   @sequoia.function(ip, port):
#   def myfunc(event, context):
#     ...
# 
# In the first way, the IP and port are taken from the event object at runtime.
#   (Henceforth, "dynamic" wrapper)
# In the second way, the IP and port are specified when myfunc is defined.
#   (Henceforth, "static" wrapper)
def function(*args):
    print("Enter function. args: {}".format(args))
    if callable(args[0]):
        return partial(_dynamic_function, args[0])
    if len(args) == 2:
        ip = args[0]
        port = int(args[1])
        def generate_static_function(lambda_handler):
            return partial(_function_wrapper, ip, port, lambda_handler)
        return generate_static_function
    else:
        raise Exception("sequoia.function should be used either as @sequoia.function or @sequoia.function(ip, port)")

