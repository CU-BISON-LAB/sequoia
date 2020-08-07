import requests
import time
from kafka import KafkaProducer
from function_chains_pb2 import LambdaFunction, ChainNode, ChainState
import numpy as np
import json
import datetime
from threading import Thread


concurrency = 1
def main():
    # NOTE: you can set invoke count of each function below the chain definitions (the concurrencies variable)
    # Long Running Function Chain
    # Chain id: 1
    # codePublish
    publish_init = LambdaFunction(url="publishinit.com", id=200)
    publish_compile = LambdaFunction(url="publishcompile.com", id=201)
    publish_compress = LambdaFunction(url="publishcompress.com", id=202)
    
    node8_publish_fan7 = ChainNode(function=publish_compile, nodeID=8, children=[], lastNodeIDs=[2, 3, 4, 5, 6, 7, 8], chainFunctionIDs=[200, 201], args = {
        "s3_input": "repos/fzf.tar.gz",
        "s3_output": "releases/fzf_test/fzf_386",
        "s3_bucket": "code-publish-bucket",
        "arch": "386",
    })
    node7_publish_fan7 = ChainNode(function=publish_compile, nodeID=7, children=[], lastNodeIDs=[2, 3, 4, 5, 6, 7, 8], chainFunctionIDs=[200, 201], args = {
        "s3_input": "repos/fzf.tar.gz",
        "s3_output": "releases/fzf_test/fzf_amd64",
        "s3_bucket": "code-publish-bucket",
        "arch": "amd64",
    })
    node6_publish_fan7 = ChainNode(function=publish_compile, nodeID=6, children=[], lastNodeIDs=[2, 3, 4, 5, 6, 7, 8], chainFunctionIDs=[200, 201], args = {
        "s3_input": "repos/fzf.tar.gz",
        "s3_output": "releases/fzf_test/fzf_arm_5",
        "s3_bucket": "code-publish-bucket",
        "arch": "arm_5",
    })
    node5_publish_fan7 = ChainNode(function=publish_compile, nodeID=5, children=[], lastNodeIDs=[2, 3, 4, 5, 6, 7, 8], chainFunctionIDs=[200, 201], args = {
        "s3_input": "repos/fzf.tar.gz",
        "s3_output": "releases/fzf_test/fzf_arm_6",
        "s3_bucket": "code-publish-bucket",
        "arch": "arm_6",
    })
    node4_publish_fan7 = ChainNode(function=publish_compile, nodeID=4, children=[], lastNodeIDs=[2, 3, 4, 5, 6, 7, 8], chainFunctionIDs=[200, 201], args = {
        "s3_input": "repos/fzf.tar.gz",
        "s3_output": "releases/fzf_test/fzf_arm_7",
        "s3_bucket": "code-publish-bucket",
        "arch": "arm_7",
    })
    node3_publish_fan7 = ChainNode(function=publish_compile, nodeID=3, children=[], lastNodeIDs=[2, 3, 4, 5, 6, 7, 8], chainFunctionIDs=[200, 201], args = {
        "s3_input": "repos/fzf.tar.gz",
        "s3_output": "releases/fzf_test/fzf_arm64",
        "s3_bucket": "code-publish-bucket",
        "arch": "arm64",
    })
    node2_publish_fan7 = ChainNode(function=publish_compile, nodeID=2, children=[], lastNodeIDs=[2, 3, 4, 5, 6, 7, 8], chainFunctionIDs=[200, 201], args = {
        "s3_input": "repos/fzf.tar.gz",
        "s3_output": "releases/fzf_test/fzf_ppc64le",
        "s3_bucket": "code-publish-bucket",
        "arch": "ppc64le",
    })
    node1_publish_fan7 = ChainNode(function=publish_init, nodeID=1, children=[node2_publish_fan7, node3_publish_fan7, node4_publish_fan7, node5_publish_fan7, node6_publish_fan7, node7_publish_fan7, node8_publish_fan7], lastNodeIDs=[2, 3, 4, 5, 6, 7, 8], chainFunctionIDs=[200, 201], args = {
        "s3_input": "repos/fzf.tar.gz",
        "arches": json.dumps([
            "386",
            "amd64",
            "arm_5",
            "arm_6",
            "arm_7",
            "arm64",
            "ppc64le"]),
    })
    chain1 = node1_publish_fan7
    
    
    
    # Medium Function Chain 1
    # Chain id: 2
    
    vidpipe_init = LambdaFunction(url="vidpipeinit.com", id=100)
    vidpipe_preview = LambdaFunction(url="vidpipepreview.com", id=101)
    vidpipe_grayscale = LambdaFunction(url="vidpipegrayscale.com", id=102)
    vidpipe_reverse = LambdaFunction(url="vidpipereverse.com", id=103)
    
    node3_vidpipe_linear_short = ChainNode(function=vidpipe_reverse, nodeID=3, children=[], lastNodeIDs=[3], chainFunctionIDs=[101, 102, 103], args = {
        "s3_input": "linear/grayscale-preview-smaller_buck_bunny-1.mp4",
        "s3_bucket": "video-pipeline-io",
        "s3_output_root": "linear/"})
    node2_vidpipe_linear_short = ChainNode(function=vidpipe_grayscale, nodeID=2, children=[node3_vidpipe_linear_short], lastNodeIDs=[3], chainFunctionIDs=[101, 102, 103], args = {
        "s3_input": "linear/preview-smaller_buck_bunny-1.mp4",
        "s3_bucket": "video-pipeline-io",
        "s3_output_root": "linear/"})
    node1_vidpipe_linear_short = ChainNode(function=vidpipe_preview, nodeID=1, children=[node2_vidpipe_linear_short], lastNodeIDs=[3], chainFunctionIDs=[101, 102, 103], args = {
        "s3_input": "big_buck_bunny/smaller_buck_bunny-1.mp4",
        "s3_bucket": "video-pipeline-io",
        "s3_output_root": "linear/"})
    chain2 = node1_vidpipe_linear_short
    
    
    
    
    # Medium Function Chain 2
    # Chain id: 3
    
    
    ## ObjectDetection using openCV
    #    L2
    #   /
    # L1
    #   \
    #    L3
    objectDetection1 = LambdaFunction(url="objectdetection1.com", id=1)
    objectDetection2 = LambdaFunction(url="objectdetection2.com", id=2)
    objectDetection3 = LambdaFunction(url="objectdetection3.com", id=3)
    node3_c6 = ChainNode(function=objectDetection3, nodeID=3, children=[], lastNodeIDs=[2,3], chainFunctionIDs=[1,2,3], args={})
    node2_c6 = ChainNode(function=objectDetection2, nodeID=2, children=[], lastNodeIDs=[2,3], chainFunctionIDs=[1,2,3], args={})
    node1_c6 = ChainNode(function=objectDetection1, nodeID=1, children=[node2_c6, node3_c6], lastNodeIDs=[2,3], chainFunctionIDs=[1,2,3], args={})
    chain3 = node1_c6

    
    
    # Short Function Chain 
    # Chain id: 4
    
    bagOfWords = LambdaFunction(url="bagofwords.com", id=300)
    node1_c4 = ChainNode(function=bagOfWords, nodeID=1, children=[], lastNodeIDs=[1], chainFunctionIDs=[1], args={})
    chain4 = node1_c4

    
    concurrencies = [
        { "chain_id": 1, "chain": chain1, "count": 1 },
        { "chain_id": 2, "chain": chain2, "count": 1 },
        { "chain_id": 3, "chain": chain3, "count": 1 },
        { "chain_id": 4, "chain": chain4, "count": 1 },
    ]
    

    no_of_invocations_long =  2 
    no_of_invocations_medium_1 = 4
    no_of_invocations_medium_2 = 3
    no_of_invocations_short = 300
    
    # chain_long = Workload("Fan2", no_of_invocations_long, concurrency, chain1, 1, 1000) // update these
    # chain_medium_1 = Workload("Linear", no_of_invocations_medium_1, concurrency, chain2, 2, 1000) // update these
    # chain_medium_2 = Workload("FanAndLinear", no_of_invocations_medium_2, concurrency, chain5, 5, 1000) // update these
    # chain_short = Workload("FanAndLinear", no_of_invocations_short, concurrency, chain5, 5, 1000) // update these
    
    chain_long_sample =[1000] #generateSample(no_of_invocations_long, concurrency)
    chain_medium_1_sample = [1000]#generateSample(no_of_invocations_medium_1, concurrency)
    chain_medium_2_sample = [1000]#generateSample(no_of_invocations_medium_2, concurrency)
    chain_short_sample =[1000]# generateSample(no_of_invocations_short, concurrency)
    
    instance_id = 0
    # Kafka connections
    kafka_url = "localhost:9092"
    producer_PQ = connect_kafka_producer(kafka_url)
    producer_PSQ = connect_kafka_producer(kafka_url)
    
    for x in range(concurrency):
        print('here')
        start = time.time()
                    
        counter_long =  chain_long_sample[x] 
        counter_medium_1 =  chain_medium_1_sample[x] 
        counter_medium_2 = chain_medium_2_sample[x] 
        counter_short = chain_short_sample[x] 
        

        while counter_long > 0 or counter_medium_1 >0 or counter_medium_2 >0  or counter_short > 0:
            
            if  counter_long > 0:
                t1 = Thread(target=startWorkload, args=(concurrencies[0]['chain'],concurrencies[0]['chain_id'], instance_id,1, producer_PQ, producer_PSQ))
                t1.start()
                counter_long-=1
            if  counter_medium_1 > 0:
                t2 = Thread(target=startWorkload, args=(concurrencies[1]['chain'],concurrencies[1]['chain_id'], instance_id,1, producer_PQ, producer_PSQ))
                t2.start()
                counter_medium_1-=1
            if  counter_medium_2 > 0:
                t3 = Thread(target=startWorkload, args=(concurrencies[2]['chain'],concurrencies[2]['chain_id'], instance_id,1, producer_PQ, producer_PSQ))
                t3.start()
                counter_medium_2-=1    
            if  counter_short > 0:
                t4 = Thread(target=startWorkload, args=(concurrencies[3]['chain'], concurrencies[3]['chain_id'], instance_id,1, producer_PQ, producer_PSQ))
                t4.start()
                counter_short-=1    
                
            instance_id += 1
        elapsed = time.time() - start
        #    print(1-elapsed)
        if 1-elapsed>0:
            time.sleep(1-elapsed)

    
def startWorkload(chain, chain_id, instance_id, requests, producer_PQ, producer_PSQ):        
    invocations = list()
    for k in range(requests):
        invocations.append(ChainState(currentNode=chain,invokeTime=str(datetime.datetime.now().isoformat('T')), instanceID=instance_id, chainID=chain_id, flags={"hybrid": ""}))
    
    pushEvents(invocations, producer_PQ, producer_PSQ)
    return
    
    
    
def pushEvents(invocations, producer_PQ, producer_PSQ):
    kafka_pq_topic = "pending_queue"
    kafka_psq_topic = "producer_side_logging_queue"

    if producer_PQ is not None:
        for invocation in invocations:
            PARAMS = { 
                "instanceId": invocation.instanceID, 
                "chainId": invocation.chainID, 
                "chainFunctionIdList": invocation.currentNode.chainFunctionIDs, 
                "extras": [{"functionPriorities":{"1":1,"2":2,"3":3}} ]
            }
            tempLog = "producerSide-start-"+str(time.time())+"-"+str(PARAMS)
            publish_message(producer_PSQ, kafka_psq_topic, 'raw', bytes(tempLog, encoding = 'utf-8'))
            publish_message(producer_PQ, kafka_pq_topic, 'raw', invocation.SerializeToString())
        
def publish_message(producer_instance, topic_name, key, value):
    try:
        key_bytes = bytes(key, encoding = 'utf-8')
        value_bytes = value
        producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
        producer_instance.flush()
        if (topic_name == "pending_queue"):
            print('Message published successfully.')
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))
    
    
def generateSample(arrival_time, sample_size):
    return np.random.poisson(arrival_time, sample_size)


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
    
