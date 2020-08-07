import numpy as np
import time
import argparse

import requests
from kafka import KafkaProducer
from function_chains_pb2 import LambdaFunction, ChainNode, ChainState

# Pushes chain invocations to a Kafka queue according to a Poisson distribution
class Workload:
    def __init__(self, name, arrival_time, sample_size, chain, chain_id, elapsed_time, ):
        # Name of the workload
        self.workload_name = name
        
        # Arrival time and sample size for poisson distribution
        self.arrival_time = arrival_time
        self.sample_size = sample_size
        
        # Function chain information
        self.chain = chain
        self.chain_id = chain_id

        # Elapsed time in seconds for the workload
        self.elapsed_time = elapsed_time 

    def startWorkload(self, producer_PQ, producer_PSQ):
        s = np.random.poisson(self.arrival_time, self.sample_size)
        # print('Samples: ', s)         
        average_inter_arrival_time = 1 / self.arrival_time         
        start_time = time.time()         
        total_samples = 0
        chain_instance_count = 0
        for i, sample in enumerate(s):
            end_time = time.time()
            elapsed_time = end_time - start_time
            if int(elapsed_time) > self.elapsed_time:
                print('{} seconds elapsed for workload {}'.format(self.elapsed_time, self.workload_name))
                return total_samples
        total_samples += sample
        invocations = list()
        for k in range(sample):
            invocations.append(ChainState(currentNode=self.chain, instanceID=chain_instance_count, chainID=self.chain_id, flags={"hybrid": ""}))
            chain_instance_count += 1
        
        self._pushEvents(invocations, producer_PQ, producer_PSQ)
        time.sleep(1 + np.random.uniform(low=-average_inter_arrival_time, high=average_inter_arrival_time, size=(1,))[0])

        return total_samples


    def _pushEvents(self, invocations, producer_PQ, producer_PSQ):
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
                self._publish_message(producer_PSQ, kafka_psq_topic, 'raw', bytes(tempLog, encoding = 'utf-8'))
                self._publish_message(producer_PQ, kafka_pq_topic, 'raw', invocation.SerializeToString())
        
    def _publish_message(self, producer_instance, topic_name, key, value):
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


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Generate Poisson workload.')
#     parser.add_argument('--arrival_time', type=int,
#                         help='average arrival time of requests in seconds', required=True)
#     parser.add_argument('--sample_size', type=int,
#                         help='size of sample to generate workload', required=True)

#     args = parser.parse_args()
#     workload(args.arrival_time, args.sample_size)
