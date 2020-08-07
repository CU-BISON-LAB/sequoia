import json
from time import sleep

from sequoia import sequoia

# Attempt to contact logging server at IP and port specified by parameters to this
# serverless function
#@sequoia.function
#def lambda_handler(event, context):

# Contact logging server at IP and port hardcoded here
@sequoia.function("10.0.0.1", 10000)
def lambda_handler(event, context):
    sleep(5)

    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda1!')
    }

