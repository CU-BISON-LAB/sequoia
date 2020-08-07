import requests
import time
from kafka import KafkaProducer
from function_chains_pb2 import LambdaFunction, ChainNode, ChainState

from workload import Workload

concurrency = 1000
# Define workloads and start each workload
def main():
    # NOTE: you can set invoke count of each function below the chain definitions (the concurrencies variable)
    # aws
    lambda1 = LambdaFunction(url="https://lambda1.com", id=1)
    lambda2 = LambdaFunction(url="https://lambda2.com", id=2)
    lambda3 = LambdaFunction(url="https://lambda3.com", id=3)
    lambda4 = LambdaFunction(url="https://lambda4.com", id=4)
    ## Chain 0 ##
    node1_c0 = ChainNode(function=lambda1, nodeID=1, children=[], lastNodeIDs=[1], chainFunctionIDs=[1], args={})
    chain0 = node1_c0
    ## Chain 1 ##
    #    L2
    #   /
    # L1
    #   \
    #    L3
    node3_c1 = ChainNode(function=lambda3, nodeID=3, children=[], lastNodeIDs=[2,3], chainFunctionIDs=[1,2,3], args={})
    node2_c1 = ChainNode(function=lambda2, nodeID=2, children=[], lastNodeIDs=[2,3], chainFunctionIDs=[1,2,3], args={})
    node1_c1 = ChainNode(function=lambda1, nodeID=1, children=[node2_c1, node3_c1], lastNodeIDs=[2,3], chainFunctionIDs=[1,2,3], args={})
    chain1 = node1_c1
    ## Chain 2 ##
    # L3-L2-L1
    node3_c2 = ChainNode(function=lambda1, nodeID=3, children=[], lastNodeIDs=[3], chainFunctionIDs=[1,2,3], args={})
    node2_c2 = ChainNode(function=lambda2, nodeID=2, children=[node3_c2], lastNodeIDs=[3], chainFunctionIDs=[1,2,3], args={})
    node1_c2 = ChainNode(function=lambda3, nodeID=1, children=[node2_c2], lastNodeIDs=[3], chainFunctionIDs=[1,2,3], args={})
    chain2 = node1_c2
    ## Chain 3 ##
    #    L2
    #   /
    # L1
    #   \
    #    L3-L4-L4-L4
    node6_c3 = ChainNode(function=lambda4, nodeID=6, children=[], lastNodeIDs=[6,2], chainFunctionIDs=[1,2,3,4,4,4], args={})
    node5_c3 = ChainNode(function=lambda4, nodeID=5, children=[node6_c3], lastNodeIDs=[6,2], chainFunctionIDs=[1,2,3,4,4,4], args={})
    node4_c3 = ChainNode(function=lambda4, nodeID=4, children=[node5_c3], lastNodeIDs=[6,2], chainFunctionIDs=[1,2,3,4,4,4], args={})
    node3_c3 = ChainNode(function=lambda3, nodeID=3, children=[node4_c3], lastNodeIDs=[6,2], chainFunctionIDs=[1,2,3,4,4,4], args={})
    node2_c3 = ChainNode(function=lambda2, nodeID=2, children=[], lastNodeIDs=[6,2], chainFunctionIDs=[1,2,3,4,4,4], args={})
    node1_c3 = ChainNode(function=lambda1, nodeID=1, children=[node2_c1, node3_c1], lastNodeIDs=[6,2], chainFunctionIDs=[1,2,3,4,4,4], args={})
    chain3 = node1_c3
    ## Chain 4 ##
    #    L2
    #   /
    # L1-L3
    #   \
    #    L4
    node4_c4 = ChainNode(function=lambda4, nodeID=4, children=[], lastNodeIDs=[2,3,4], chainFunctionIDs=[1,2,3,4], args={})
    node3_c4 = ChainNode(function=lambda3, nodeID=3, children=[], lastNodeIDs=[2,3,4], chainFunctionIDs=[1,2,3,4], args={})
    node2_c4 = ChainNode(function=lambda2, nodeID=2, children=[], lastNodeIDs=[2,3,4], chainFunctionIDs=[1,2,3,4], args={})
    node1_c4 = ChainNode(function=lambda1, nodeID=1, children=[node2_c4, node3_c4, node4_c4], lastNodeIDs=[2,3,4], chainFunctionIDs=[1,2,3,4], args={})
    chain4 = node1_c4
    ## Chain 5 ##
    #    L2
    #   /
    # L1
    #   \
    #    L3-L3
    node4_c5 = ChainNode(function=lambda3, nodeID=4, children=[], lastNodeIDs=[4,2], chainFunctionIDs=[1,2,3,3], args={})
    node3_c5 = ChainNode(function=lambda3, nodeID=3, children=[node4_c5], lastNodeIDs=[4,2], chainFunctionIDs=[1,2,3,3], args={})
    node2_c5 = ChainNode(function=lambda2, nodeID=2, children=[], lastNodeIDs=[4,2], chainFunctionIDs=[1,2,3,3], args={})
    node1_c5 = ChainNode(function=lambda1, nodeID=1, children=[node2_c5, node3_c5], lastNodeIDs=[4,2], chainFunctionIDs=[1,2,3,3], args={})
    chain5 = node1_c5

    ######################################################################################################################
    # NOTE: real applications
    ## ObjectDetection using openCV 
    #    L2
    #   /
    # L1
    #   \
    #    L3
    objectDetection1 = LambdaFunction(url="image-preprocessing.com", id=1)
    objectDetection2 = LambdaFunction(url="opencv_maskrcnn.com", id=2)
    objectDetection3 = LambdaFunction(url="opencv_yolo.com", id=3)
    node3_c6 = ChainNode(function=objectDetection3, nodeID=3, children=[], lastNodeIDs=[2,3], chainFunctionIDs=[1,2,3], args={})
    node2_c6 = ChainNode(function=objectDetection2, nodeID=2, children=[], lastNodeIDs=[2,3], chainFunctionIDs=[1,2,3], args={})
    node1_c6 = ChainNode(function=objectDetection1, nodeID=1, children=[node2_c6, node3_c6], lastNodeIDs=[2,3], chainFunctionIDs=[1,2,3], args={})
    chain6 = node1_c6

    concurrencies = [
        {"chain": chain0, "count": 0},
        {"chain": chain1, "count": 1},
        {"chain": chain2, "count": 1},
        {"chain": chain3, "count": 0},
        {"chain": chain4, "count": 0},
        {"chain": chain5, "count": 1},
        {"chain": chain6, "count": 0},
    ]

    chain_fan2 = Workload("Fan2", 5, 20, chain1, 1, 1000)
    chain_linear = Workload("Linear", 5, 20, chain2, 2, 1000)
    chain_fan_linear = Workload("FanAndLinear", 5, 20, chain5, 5, 1000)

    # Set up Kafka
    # kafka_url = "localhost:9092"
    # kafka_pq_topic = "pending_queue"
    # producer_PQ = connect_kafka_producer(kafka_url)
    # # Producer Side Logging
    # kafka_psq_topic = "producer_side_logging_queue" 
    # producer_PSQ = connect_kafka_producer(kafka_url)

    # Functions are invoked here
    chain_fan2.startWorkload(producer_PQ, producer_PSQ)
    chain_linear.startWorkload(producer_PQ, producer_PSQ)
    chain_fan_linear.startWorkload(producer_PQ, producer_PSQ)

    producer_PQ.close()
    producer_PSQ.close()


# Establish connection to the Kafka server
def connect_kafka_producer(url):
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=[url], api_version=(0, 10))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return _producer

if __name__ == '__main__':
    main()
