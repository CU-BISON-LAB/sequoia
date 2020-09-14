# Sequoia Producer

## DAG Creation and Usage

In the Producer, we define DAGs for each function chain that we intend to invoke. 
The DAGs are defined using Protocol Buffer message classes, which are documented 
in `sequoia/protobufs/README.md`. In short, a DAG is composed of one or more 
`ChainNode`s, each of which points to a `LambdaFunction` that it should invoke.

For every function chain invocation, a `ChainState` is instantiated to point to 
the start of the function chain DAG. (Later, in the Consumer, `ChainState`s are 
used to track where we are in the DAG at any point in time while a function chain 
is executing.)

Because DAGs and `ChainState`s are defined as Protocol Buffer messages, they are 
easy to serialize and push into Kafka queues. We can simply call 
`invocation.SerializeToString()` and pass that as the body of our Kafka message. 
On the consumer, it is similarly easy to deserialize.

