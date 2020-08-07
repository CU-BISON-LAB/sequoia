# Sequoia Function Wrapper

To use Sequoia for function logging, it should be called like this:

```python  
from sequoia import sequoia

@sequoia.function
def lambda_handler(event, context):
  ...
```

This will send logs for function timings to the server specified by `(event["ip"], event["port"])`. If, for some reason, the IP and port should be hard-coded in this lambda function, then the following can be written instead:

```python  
from sequoia import sequoia

@sequoia.function("10.0.0.1", 10000)
def lambda_handler(event, context):
  ...
```

As hinted by the syntax of the above examples, the function wrapper is currently 
implemented for AWS Lambda. This is straightforward to change for other 
serverless platforms: replace references to `event` and `context` in 
`sequoia.py` with the equivalents for the target platform
