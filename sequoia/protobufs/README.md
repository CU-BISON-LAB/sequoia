To update the definitions of lambda functions, etc., update `function_chains.proto` and run the below command to regenerate `function_chains_pb2.py`. The protobuf compiler must be installed (`sudo snap install protobuf` or from here: `https://github.com/protocolbuffers/protobuf/releases/download/v3.11.1/protoc-3.11.1-linux-x86_64.zip`) for this to work.

To regenerate `function_chains_pb2.py`:  
`protoc -I=. --python_out=. ./function_chains.proto`

To import the generated python code, first run `pip install google protobuf` if these are not already installed. 
