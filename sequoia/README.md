# Sequoia

Source code for the implementation of Sequoia. 

Refer to the Architecture section of our paper for a detailed description of the 
architecture of Sequoia. Each component of the architecture maps to certain 
parts of the source code, as described in the **Folder 
Hierarchy** below. 

All of the scheduling policies we have implemented here make decisions when 
pulling chain invocations out of Kafka queues, in the Policy Framework component 
of the Consumer script. If multiple queues are needed to implement a new policy, 
the queue placement logic in `serial_consumer.py:enqueue_invocation(...)`

## Dependencies

* Python 3.6+ with the following packages:  
  * [Python Kafka client](https://pypi.org/project/kafka/)  
  * [Requests](https://pypi.org/project/requests/)  
  * [Protobufs](https://pypi.org/project/protobuf/)  
  * [NumPy](https://pypi.org/project/numpy/)  
* An [Apache Kafka](https://kafka.apache.org/) deployment 

## Folder Hierarchy

### producer/

Contains the implementation of the Producer, which is part of the QoS Scheduler. 
For our experiments, we defined all of our workloads and function chain DAGs 
directly in this file. The Producer pushes function invocations into Kafka 
queues for the Consumer to read.

There are two variants: one that supports a burst or continuous fixed size 
workload (`serial_producer.py`), and one that supports a Poisson distribution 
based workload (`poisson_producer.py`).

Both producer scripts contain some example function chain DAGs, such as a fan-7 chain that compiles [fzf](https://github.com/junegunn/fzf) to 7 different computer 
architectures. URLs have been omitted, so one must deploy their own functions to use Sequoia.

### consumer/

Contains the implementation of the Resource Manager, Logging Framework, and 
Policy Framework. It reads from the Kafka queues to schedule and invoke 
serverless functions on a pool of worker threads, while tracking function 
logging and metrics in a separate thread.

### function-logger/

Contains the code for function-side logging on Sequoia. Currently implemented to 
support AWS Lambda, but supporting other platforms is as simple as changing the 
function wrapper to use the serverless platforms' main function arguments (for 
example, AWS Lambda functions use `lambda_handler(event, context)`, so the 
wrapper must use `event` and `context`).

### spammers/

Contains scripts for invoking batches of serverless functions without Sequoia's 
rate limiting. If the functions are gathering logs, the Sequoia consumer must 
still be running when the spammer invokes the functions. Otherwise, the 
functions will fail because they do not have a logging framework to connect to.

### protobufs/

Contains the protobuf definitions and the Python output of the Protobuf compiler.

## Running the code

Deploy HTTP serverless functions on the serverless platform of your choice and 
describe the DAGs of your function chains inside of the Producer.

To run with Sequoia's QoS features, make sure your Kafka deployment is 
accessible by both the Producer and the Consumer and start the Consumer first, 
then the Producer. The Producer will push to Kafka queues which are then read by 
the Consumer and invoked. 

To run without Sequoia's QoS features, run the consumer (still needed for 
gathering metrics) and start one of the spammers. 

To run the producer and consumer, either add `protobufs/` to your `PYTHONPATH` 
or copy `function_chains_pb2.py` directly into the `producer/` and `consumer/` 
folders.
