# Protocol Buffers in Sequoia

The messages defined in `function_chains.proto` represent everything needed to 
express function chain DAGs and invocations in Sequoia. A DAG is composed of
ChainNodes which contain unique nodeIDs and correspond to specific Lambda
Functions that they invoke. 

When we make an invocation in the Producer, a ChainState object is created to
represent the invocation. The ChainState is essentially a pointer into a DAG,
but it also includes instance IDs and chain IDs to uniquely distinguish the
invocation from other invocations.

The ChainNode and ChainState messages also contain non-stateful data, such as
the ChainNode's set of all function IDs that exist inside the chain, which could
be refactored in the future so that they are not duplicated for every ChainState 
and/or ChainNode.

To update the definitions of a Protobuf message type, update 
`function_chains.proto` and run the below command to regenerate 
`function_chains_pb2.py`. The protobuf compiler must support `proto3` syntax, 
which can be installed using snap (`sudo snap install protobuf`) or from one of 
the official releases like this one 
(`https://github.com/protocolbuffers/protobuf/releases/download/v3.11.1/protoc-3.11.1-linux-x86_64.zip`) for this to work.

To regenerate `function_chains_pb2.py`:  
`protoc -I=. --python_out=. ./function_chains.proto`

To import the generated python code, first run `pip install google protobuf` if these are not already installed. 
