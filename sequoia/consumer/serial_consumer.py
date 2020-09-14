import time
import json
import queue
import socket
import requests 
import threading
from sys import exit
from threading import Thread
from kafka import KafkaConsumer, KafkaProducer
from function_chains_pb2 import ChainState
from concurrent.futures import ThreadPoolExecutor

# Configuration

# Set to True to disable invoking serverless functions for testing
mock_invocations = True

# ip/port to listen on
logger_port = 10000
serverIp = "127.0.0.1"

# Scheduling Policies
# Uncomment only the desired policy
# Note that the simpleQueuePriorityPolicy requires the enqueue_simple_priority
# queueing policy to work.
# All other existing policies require enqueue_pending_or_running.
def scheduling_policy():
    return currentlyRunningChainsPolicy()
    #return getShortestJobFirst()
    #return fairShareOnChainsPolicy()
    #return fairShareOnFunctionsPolicy()
    #return strictFunctionPriorityPolicy()
    #return hybridBinPackingPolicy()
    #return simpleQueuePriorityPolicy()

# Queueing Policies
# Uncomment only the desired policy
# The only scheduling policy that needs enqueue_simple_priority is
# simpleQueuePriorityPolicy, all others require enqueue_pending_or_running
def enqueue_invocation(invocation, chainAlreadyRunning):
    return enqueue_pending_or_running(invocation, chainAlreadyRunning)
    #return enqueue_simple_priority(invocation, chainAlreadyRunning)

# hybrid clouds
localCloudConcurrency = threading.Semaphore(200)

# logging details
chains_records = []
functions_records = []
logging_running_records = []
logging_finished_records = []

# arrivalRateQueue length
arrivalRateQueueLength = 30
# kafka queue timeout in milliseconds
kafkaTimeOut = 10
kafkaPQSoftLimit = 100
kafkaCRQSoftLimit = 100
# kafka queue length
kafkaCRQLength = 0
# in memory queue size
queueSize = 1000000
inMemorySleep = 0.0005

# threading details
fsMetricServerLock = threading.Lock()
csMetricServerLock = threading.Lock()
psMetricServerLock = threading.Lock()
kafkaCRQLengthLock = threading.Lock()
raceConditionLock = threading.Lock()
lockFunctionSideLogger = threading.Lock()
concurrency = 1000
threadPool = 1000
pool = threading.Semaphore(threadPool)
concurrencyPool = threading.Semaphore(concurrency)

# SJF dictionary - format (chainId, nodeId): average remaining runtime
SJFLookup = { (1,1): 20.2,
              (1,2): 20,
              (1,3): 20,
              (2,1): 39,
              (2,2): 19,
              (2,3): 2,
              (3,1): 37.2,
              (3,2): 20,
              (3,3): 37,
              (3,4): 17}

# Main scheduling loop. After initializing a worker thread pool,
# we invoke the Policy Framework to choose the next function to invoke, then invoke it.
def schedule_invocations():
    executor = ThreadPoolExecutor(max_workers=threadPool)
    iter = 0
    while(True):
        timeStampList = []
        timeStampList.append(iter) 
        timeStampList.append(time.time())

        # Select a function to invoke
        choice = scheduling_policy()

        timeStampList.append(time.time())
        # If a choice was made, submit it to the worker pool to execute
        # Else, continue the loop
        if (choice != None):
            iter = iter + 1
            raceConditionLock.acquire()
            timeStampList.append(time.time())
            executor.submit(invoker_thread, choice, timeStampList)

# Function Side Metric Server
# Only this or the consumer side metric server should call updateRecords(timeStamp)
def fsMetricServer():
  while(True):
    time.sleep(inMemorySleep)
    if not(inMemoryFSQ.empty()):
      timeStamp = inMemoryFSQ.get()
      #print(timeStamp)
      #updateRecords(timeStamp)
      #print(metricServer.collectiveFunctionLevelMetric, metricServer.collectiveChainLevelMetric)

# Consumer Side Metric Server
# Only this or the function side metric server should call updateRecords(timeStamp)
def csMetricServer():
  while(True):
    time.sleep(inMemorySleep)
    timeStamp = ""
    if not(inMemoryCSSQ.empty()):
      timeStamp = inMemoryCSSQ.get()
    elif not(inMemoryCSEQ.empty()):
      timeStamp = inMemoryCSEQ.get()
    if (timeStamp != ""):
      inMemoryCSL.put(timeStamp)
      updateRecords(timeStamp)
      print(metricServer.collectiveFunctionLevelMetric, metricServer.collectiveChainLevelMetric)
      temp = json.loads(timeStamp.decode("utf-8").split("-")[3].replace("'", "\""))
      #print(metricServer.individualFunctionMetricList[0]['instancesRunning'], time.time())

# Producer side metric server
# Processes metrics produced by the producer
def psMetricServer():
  while(True):
    time.sleep(inMemorySleep)
    if not(inMemoryPSQ.empty()):
      timeStamp = inMemoryPSQ.get()
      updateArrivalRecords(timeStamp)

# Read Kafka messages into the in-memory pending queue for performance
def kafkaToInMemoryPQ():
  while(True):
    msg = consumer_PQ._poll_once(timeout_ms=kafkaTimeOut, max_records=1)
    if (msg):
      #print("kafka to memory")
      for key,value in msg.items():
        timeStamp = value[0].value
        enqueue_invocation(timeStamp, chainAlreadyRunning=False)

# Read Kafka messages into the in-memory producer queue for performance
def kafkaToInMemoryPSQ():
  while(True):
    msg = consumer_PSQ._poll_once(timeout_ms=kafkaTimeOut, max_records=1)
    if (msg):
      #print("kafka to memory")
      for key,value in msg.items():
        timeStamp = value[0].value
        inMemoryPSQ.put(timeStamp)

# Update function chain arrival metrics with a new timestamp
def updateArrivalsChainsMetricList(timeStamp):
  psMetricServerLock.acquire()
  newChainEntry = True
  for i in metricServer.arrivalsChainsMetricList:
    if (i['chainId'] == timeStamp.chainId):
      newChainEntry = False
      i['arrivalRateQueue'].append(timeStamp.start)
      if (len(i['arrivalRateQueue']) > arrivalRateQueueLength):
        i['arrivalRateQueue'].pop(0)
      timeDifference = i['arrivalRateQueue'][-1] - i['arrivalRateQueue'][0]
      i['arrivalRate'] = len(i['arrivalRateQueue'])/timeDifference
  if (newChainEntry):
    tempDictionary = { 'chainId': timeStamp.chainId,
	'arrivalRateQueue': [timeStamp.start],
	'arrivalRate': 0,
        'chainFunctionIdList': timeStamp.chainFunctionIdList}
    metricServer.arrivalsChainsMetricList.append(tempDictionary)
  psMetricServerLock.release()

# Update function specific metrics with a new timestamp
def updateIndividualFunctionMetricList(timeStamp):
  newEntry = True
  for i in metricServer.individualFunctionMetricList:
    if (i['functionId'] == timeStamp.functionId):
      newEntry = False
      if (timeStamp.finish == 'running'):
        if (timeStamp.chainId not in i['chainIdList']):
          i['chainIdList'].append(timeStamp.chainId)
        i['instancesRunning'] = i['instancesRunning'] + 1
      else:
        i['instancesRunning'] = i['instancesRunning'] - 1
        i['instancesCompleted'] = i['instancesCompleted'] + 1
        i['avgRuntime'] = (i['avgRuntime']*(i['instancesCompleted']-1)+(timeStamp.finish-timeStamp.start))/i['instancesCompleted']
  if (newEntry):
    tempDictionary = { 'functionId': timeStamp.functionId,
      'chainIdList': [timeStamp.chainId],
      'instancesRunning': 1,
      'instancesCompleted': 0,
      'avgRuntime': 0}
    metricServer.individualFunctionMetricList.append(tempDictionary)

# Update aggregate metrics with a new timestamp
def updateCollectiveFunctionLevelMetrics(timeStamp):
  if (timeStamp.finish == 'running'):
    metricServer.collectiveFunctionLevelMetric['totalRunningFunctions'] = metricServer.collectiveFunctionLevelMetric['totalRunningFunctions'] + 1
  else:
    metricServer.collectiveFunctionLevelMetric['totalRunningFunctions'] = metricServer.collectiveFunctionLevelMetric['totalRunningFunctions'] - 1
    metricServer.collectiveFunctionLevelMetric['totalCompletedFunctions'] = metricServer.collectiveFunctionLevelMetric['totalCompletedFunctions'] + 1

# Update function chain specific metrics with a new timestamp
def updateIndividualChainLevelMetrics(timeStamp):
  newChainEntry = True
  for i in metricServer.individualChainMetricList:
    if (i['chainId'] == timeStamp.chainId):
      newChainEntry = False
      newInstanceEntry = True
      for j in i['uniqueInstanceList']:
        if ((timeStamp.chainId, timeStamp.instanceId) == j['uid']):
          newInstanceEntry = False
          if (timeStamp.finish != 'running'):
            i['functionsRunning'] = i['functionsRunning'] - 1
          else:
            i['functionsRunning'] = i['functionsRunning'] + 1
          if (timeStamp.nodeId in j['lastNodeIdList'] and timeStamp.finish != 'running'):
            j['lastNodeIdList'].remove(timeStamp.nodeId)
          if (len(j['lastNodeIdList']) < 1):
            j['endTime'] = time.time()
            i['instancesRunning'] = i['instancesRunning'] - 1
            i['instancesCompleted'] = i['instancesCompleted'] + 1
            runtime = j['endTime']-j['startTime']
            i['avgRuntime'] = (i['avgRuntime']*(i['instancesCompleted']-1)+runtime)/i['instancesCompleted']
      if (newInstanceEntry):
        tempDictionary = {
         'uid': (timeStamp.chainId, timeStamp.instanceId),
         'startTime': time.time(),
         'endTime': 'running',
         'lastNodeIdList': timeStamp.lastNodeIdList}
        i['uniqueInstanceList'].append(tempDictionary)
        i['instancesRunning'] = i['instancesRunning'] + 1
        i['functionsRunning'] = i['functionsRunning'] + 1
  if (newChainEntry):
    tempDictionary = { 'chainId': timeStamp.chainId,
      'uniqueInstanceList': [{
         'uid': (timeStamp.chainId, timeStamp.instanceId),
         'startTime': time.time(),
         'endTime': 'running',
         'lastNodeIdList': timeStamp.lastNodeIdList}],
      'chainFunctionIDs': timeStamp.chainFunctionIdList,
      'instancesRunning': 1,
      'functionsRunning': 1,
      'instancesCompleted': 0,
      'avgRuntime': 0}
    metricServer.individualChainMetricList.append(tempDictionary)

# Update aggregate function chain metrics
def updateCollectiveChainLevelMetrics():
  totalRunning = 0
  totalCompleted = 0
  for i in metricServer.individualChainMetricList:
    totalRunning = totalRunning + i['instancesRunning']
    totalCompleted = totalCompleted + i['instancesCompleted']
  metricServer.collectiveChainLevelMetric['totalRunningChains'] = totalRunning
  metricServer.collectiveChainLevelMetric['totalCompletedChains'] = totalCompleted

# Update all instantaneous state metrics with a new timestamp
def updateStateObjects(timeStamp):
  csMetricServerLock.acquire()
  updateIndividualFunctionMetricList(timeStamp)
  updateCollectiveFunctionLevelMetrics(timeStamp)
  updateIndividualChainLevelMetrics(timeStamp)
  updateCollectiveChainLevelMetrics()
  csMetricServerLock.release()
  if (raceConditionLock.locked() and timeStamp.finish == 'running'):
    raceConditionLock.release()

# Update all arrival related metrics with a new timestamp
def updateArrivalRecords(item):
  #temp = item.split("-")
  ## in-Memory
  temp = item.decode("utf-8").split("-")
  tempDictionary = json.loads(temp[3].replace("'", "\""))
  #tempDictionary['chainFunctionIdList'] = json.loads(tempDictionary['chainFunctionIdList'])
  timestamp = TimeStamp(float(temp[2]), 'running', temp[0], tempDictionary['instanceId'],
	tempDictionary['chainId'], 'NA', 'NA', 'NA', tempDictionary['chainFunctionIdList'])
  csMetricServerLock.acquire()
  updateArrivalsChainsMetricList(timestamp)
  updateFairShareFunctionQuota()
  updateFunctionPriorities(tempDictionary['extras'])
  updateChainPriorities(tempDictionary['extras'])
  csMetricServerLock.release()

# Update function priorities for reactive priority scheduling
def updateFunctionPriorities(timestamp):
  if ('functionPriorities' in timestamp[0]):
    for key, value in sorted(timestamp[0]['functionPriorities'].items()):
      metricServer.functionPrioritiesList.append(int(key))
      #print(key,value)

# Update chain priorities for reactive priority scheduling
def updateChainPriorities(timestamp):
  if ('chainPriorities' in timestamp[0]):
    for key, value in sorted(timestamp[0]['chainPriorities'].items()):
      metricServer.chainPrioritiesList.append(int(key))
      #print(key,value)

# Update log data structures according to the input log text
def updateRecords(item):
    temp = item.decode("utf-8").split("-")
    if (temp[1] == 'start'):
      tempDictionary = json.loads(temp[3].replace("'", "\""))
      tempDictionary['lastNodeIdList'] = json.loads(tempDictionary['lastNodeIdList'])
      tempDictionary['chainFunctionIdList'] = json.loads(tempDictionary['chainFunctionIdList'])
      timestamp = TimeStamp(float(temp[2]), 'running', temp[0], tempDictionary['instanceId'],
                            tempDictionary['chainId'], tempDictionary['functionId'], tempDictionary['nodeId'],
                            tempDictionary['lastNodeIdList'], tempDictionary['chainFunctionIdList'])
      logging_running_records.append(timestamp)
      updateStateObjects(timestamp)
    elif (temp[1] == 'end'):
      tempDictionary = json.loads(temp[3].replace("'", "\""))
      for i in logging_running_records:
        if (i.type==temp[0] and i.instanceId==tempDictionary['instanceId'] and i.chainId==tempDictionary['chainId'] and
            i.functionId==tempDictionary['functionId'] and i.nodeId==tempDictionary['nodeId']):
          i.finish = float(temp[2])
          logging_finished_records.append(i)
          logging_running_records.remove(i)
          #print(tempDictionary)
          updateStateObjects(i)
          break
    #printLoggingLists()

# Consumer side logging thread
def csLogging():
  while(True):
    time.sleep(inMemorySleep)
    if not(inMemoryCSL.empty()):
      timeStamp = inMemoryCSL.get().decode("utf-8")
      with open("serverLogsCS.txt", "a") as logfile:
        logfile.write(str(timeStamp)+'\n')


# Function side logging thread
def fsLogging():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = (serverIp, logger_port)
    # Listen for incoming connections
    sock.bind(server_address)
    sock.listen(15000)
    count =0
    print('starting Logger up on', server_address)
    while True:
        # Wait for a connection
        connection, client_address = sock.accept()
        try:
            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(1024)
                data = data.decode("utf-8")
                if data != '':
                    lockFunctionSideLogger.acquire()
                    with open("serverLogs.txt", "a") as logfile:
                        logfile.write(str(data))
                        count = count + 1
#                        print(str(data), count)
                        #update_records(str(data))
                        #publish_message(producer_FSQ, kafka_fsq_topic, 'raw', bytes(data, encoding = 'utf-8'))
                        ## in-Memory
                        inMemoryFSQ.put(bytes(data, encoding = 'utf-8'))
                    lockFunctionSideLogger.release()
                if not data:
                    # print('no more data from', client_address)
                    break
        finally:
            # Clean up the connection
            connection.close()

# Entry point for worker threads
# Invokes a serverless function, then queues any children that need to be
# invoked after completion, according to the function chain's DAG
def invoker_thread(chain, timeStampList):
    timeStampList.append(time.time())

    # Get required information
    url = chain.currentNode.function.url
    instanceId = chain.instanceID
    chainId = chain.chainID
    functionId = chain.currentNode.function.id
    nodeId = chain.currentNode.nodeID
    lastNodeIdList = chain.currentNode.lastNodeIDs
    chainFunctionIdList = chain.currentNode.chainFunctionIDs
    hybrid = chain.flags["hybrid"]

    # Build array of parameters to send to the function
    # (mostly needed for uniquely identifying log messages)
    PARAM = {"instanceId": instanceId,
              "chainId": chainId,
              "functionId": functionId,
              "nodeId": nodeId,
              "lastNodeIdList": str(lastNodeIdList),
              "extras": [],
              "chainFunctionIdList": str(chainFunctionIdList),
              "hybrid": hybrid,
              "id": 0}
    PARAMS = {"id":str(PARAM),"port":logger_port,"ip":serverIp,"name":"functionSide"}

    timeStampList.append(time.time())
    timeStamp = 'consumerSide-start-'+str(time.time())+'-'+str(PARAM)
    inMemoryCSSQ.put(bytes(timeStamp, encoding = 'utf-8'))
    timeStampList.append(time.time())

    # Do the invocation
    if not mock_invocations:
        res = requests.post(url = url, json = PARAMS, timeout = 300)
    else:
        print("Invoke:", url)
        time.sleep(5)

    timeStampList.append(time.time())

    timeStamp = 'consumerSide-end-'+str(time.time())+'-'+str(PARAM)
    inMemoryCSEQ.put(bytes(timeStamp, encoding = 'utf-8'))
    timeStampList.append(time.time())
    newInvocations = []

    # Enqueue children to be invoked later by the scheduler
    for i in chain.currentNode.children:
      newInvocations.append(ChainState(currentNode=i, instanceID=instanceId, chainID=chainId))
    for invocation in newInvocations:
      enqueue_invocation(invocation.SerializeToString(), chainAlreadyRunning=True)

    if hybrid == "local":
      localCloudConcurrency.release()
    timeStampList.append(time.time())

def enqueue_pending_or_running(invocation, chainAlreadyRunning):
    if chainAlreadyRunning:
        inMemoryCRQ.put(invocation)
    else:
        inMemoryPQ.put(invocation)

def enqueue_simple_priority(invocation, chainAlreadyRunning):
    chain_state = inMemory_to_chain_state(invocation)
    if chain_state is None:
        return
    if chain_state.chainID % 2 == 0:
        inMemoryHighPriorityQueue.put(invocation)
    else:
        inMemoryLowPriorityQueue.put(invocation)

# Create a connection to the Kafka server
def connect_kafka_producer(url):
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=[url], api_version=(0, 10))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return _producer

# Publish a message to a Kafka queue
def publish_message(producer_instance, topic_name, key, value):
    try:
        key_bytes = bytes(key, encoding = 'utf-8')
        value_bytes = value
        producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
        producer_instance.flush()
        #print('Message published successfully.')
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))

# Convert a Kafka message to a Chain State object
def message_to_chain_state(message):
    if (message):
        for key,value in message.items():
            serialized_chain = value[0].value
        chain_state = ChainState()
        chain_state.ParseFromString(serialized_chain)
        return chain_state
    else:
        return None

# Convert a queue item to a Chain State object
def inMemory_to_chain_state(message):
    if (message):
        chain_state = ChainState()
        chain_state.ParseFromString(message)
        return chain_state
    else:
        return None


def printLoggingLists():
    print("\nrunning records list")
    for i in logging_running_records:
      print(i.printTimeStamp())
    print("finished records list")
    for i in logging_finished_records:
      print(i.printTimeStamp())

# Class to represent all metadata associated with a timestamp
class TimeStamp:
  def __init__(self, start, finish, type, instanceId, chainId, functionId, nodeId, lastNodeIdList, chainFunctionIdList):
    self.start = start
    self.finish = finish
    self.type = type
    self.instanceId = instanceId
    self.chainId = chainId
    self.functionId = functionId
    self.nodeId = nodeId
    self.lastNodeIdList = lastNodeIdList
    self.chainFunctionIdList = chainFunctionIdList
  def printTimeStamp(self):
    return str(self.start)+"-"+str(self.finish)+"-"+str(self.type)+"-"+str(self.instanceId)+"-"+str(self.chainId)+"-"+str(self.functionId)+"-"+str(self.nodeId)+"-"+str(self.lastNodeIdList)

# Class representing the Metric Server state
class MetricServer:
  def __init__(self):
    self.collectiveFunctionLevelMetric = {
      'totalRunningFunctions': 0,
      'totalCompletedFunctions': 0
    }
    self.collectiveChainLevelMetric = {
      'totalRunningChains': 0,
      'totalCompletedChains': 0
    }
    self.functionQuotas = {}
    self.functionPrioritiesList = []
    self.chainPrioritiesList = []
    self.arrivalsChainsMetricList = []
    self.individualFunctionMetricList = []
    self.individualChainMetricList = []
  # collective Function Level Metrics
  def getTotalRunningFunctions(self):
    return self.collectiveFunctionLevelMetric['totalRunningFunctions']
  # collective Chain Level Metrics
  # individual function Level Metrics
  def getTotalUniqueFunctions(self):
    return len(self.individualFunctionMetricList)
  def getUniqueFunctionsList(self):
    return self.individualFunctionMetricList
  # individual chain level Metrics
  def getTotalUniqueChains(self):
    return len(self.individualChainMetricList)
  def getUniqueChainsList(self):
    return self.individualChainMetricList

# Currently Running Chains Policy:
# Prioritize finishing function chains that have already started running
# over those that have not started
def currentlyRunningChainsPolicy():
  time.sleep(inMemorySleep)
  if not(inMemoryCRQ.empty()):
    msg = inMemoryCRQ.get()
    chain = inMemory_to_chain_state(msg)
    return chain
  else:
    if not(inMemoryPQ.empty()):
      chain = inMemory_to_chain_state(inMemoryPQ.get())
      return chain
    else:
      return None

# Fair Share on Chains Policy:
# Assign a fixed concurrency limit to all function chains
def fairShareOnChainsPolicy():
  global previousState
  time.sleep(inMemorySleep)
  softLimitCRQ = kafkaCRQSoftLimit
  softLimitPQ = kafkaPQSoftLimit
  chainsToAvoid = getCandidateChainsAlreadyUsedQuota()
  if (chainsToAvoid == []):
    return currentlyRunningChainsPolicy()
  while(softLimitCRQ > 0):
    if not(inMemoryCRQ.empty()):
      msg = inMemoryCRQ.get()
      chain = inMemory_to_chain_state(msg)
      softLimitCRQ = softLimitCRQ - 1
      if (chain.chainID not in chainsToAvoid):
        return chain
      else:
        inMemoryCRQ.put(msg)
    else:
      softLimitCRQ = 0
  while(softLimitPQ > 0):
    if not(inMemoryPQ.empty()):
      msg = inMemoryPQ.get()
      chain = inMemory_to_chain_state(msg)
      softLimitPQ = softLimitPQ - 1
      if (chain.chainID not in chainsToAvoid):
        return chain
      else:
        inMemoryPQ.put(msg)
    else:
      softLimitPQ = 0
  return None

# Returns a list of function chains that fully saturate their respective
# concurrency limits.
def getCandidateChainsAlreadyUsedQuota():
  csMetricServerLock.acquire()
  candidateList = []
  for i in metricServer.getUniqueChainsList():
    if (i['functionsRunning'] >= round(concurrency/metricServer.getTotalUniqueChains())):
      candidateList.append(i['chainId'])
  csMetricServerLock.release()
  return candidateList

# Shortest Job First Policy:
# Returns the queued chain invocation with the least time remaining
# (Currently, simply based on historical average runtimes)
def getShortestJobFirst():
  time.sleep(inMemorySleep)
  # variables
  softLimitCRQ = kafkaCRQSoftLimit
  softLimitPQ = kafkaPQSoftLimit
  msg_baseCase = ''
  chain_baseCase = ''
  while(softLimitCRQ > 0):
    if not(inMemoryCRQ.empty()):
      # getting first object
      if msg_baseCase == '':
        msg_baseCase = inMemoryCRQ.get()
        chain_baseCase = inMemory_to_chain_state(msg_baseCase)
      else:
        msg = inMemoryCRQ.get()
        chain = inMemory_to_chain_state(msg)
        softLimitCRQ = softLimitCRQ - 1
#        print((chain.chainID,chain.currentNode.nodeID), (chain_baseCase.chainID,chain_baseCase.currentNode.nodeID))
        if (SJFLookup[(chain.chainID,chain.currentNode.nodeID)] < SJFLookup[(chain_baseCase.chainID,chain_baseCase.currentNode.nodeID)]):
          inMemoryCRQ.put(msg_baseCase)
          msg_baseCase = msg
          chain_baseCase = chain
#          print('updated baseCase')
        else:
          inMemoryCRQ.put(msg)
#          print('no update')
        if (softLimitCRQ == 1):
          return chain_baseCase
    else:
      softLimitCRQ = 0
  while(softLimitPQ > 0):
    if not(inMemoryPQ.empty()):
      if msg_baseCase == '':
        msg_baseCase = inMemoryPQ.get()
        chain_baseCase = inMemory_to_chain_state(msg_baseCase)
      else:
        msg = inMemoryPQ.get()
        chain = inMemory_to_chain_state(msg)
        softLimitPQ = softLimitPQ - 1
#        print((chain.chainID,chain.currentNode.nodeID), (chain_baseCase.chainID,chain_baseCase.currentNode.nodeID))
        if (SJFLookup[(chain.chainID,chain.currentNode.nodeID)] < SJFLookup[(chain_baseCase.chainID,chain_baseCase.currentNode.nodeID)]):
          inMemoryPQ.put(msg_baseCase)
          msg_baseCase = msg
          chain_baseCase = chain
#          print('updated baseCase')
        else:
          inMemoryPQ.put(msg)
#          print('no update')
        if (softLimitPQ == 1):
          return chain_baseCase
    else:
      softLimitPQ = 0
  if (chain_baseCase != ''):
    return chain_baseCase
  return None


# Fair Share on Functions Policy:
# Assign a fixed concurrency limit to all function types that can be invoked
def fairShareOnFunctionsPolicy():
  time.sleep(inMemorySleep)
  softLimitCRQ = kafkaCRQSoftLimit
  softLimitPQ = kafkaPQSoftLimit
  functionsToAvoid = getCandidateFunctionsAlreadyUsedQuota()
  if (functionsToAvoid == []):
    return currentlyRunningChainsPolicy()
  while(softLimitCRQ > 0):
    if not(inMemoryCRQ.empty()):
      msg = inMemoryCRQ.get()
      chain = inMemory_to_chain_state(msg)
      softLimitCRQ = softLimitCRQ - 1
      if (chain.currentNode.function.id not in functionsToAvoid):
        return chain
      else:
        inMemoryCRQ.put(msg)
    else:
      softLimitCRQ = 0
  while(softLimitPQ > 0):
    if not(inMemoryPQ.empty()):
      msg = inMemoryPQ.get()
      chain = inMemory_to_chain_state(msg)
      softLimitPQ = softLimitPQ - 1
      if (chain.currentNode.function.id not in functionsToAvoid):
        return chain
      else:
        inMemoryPQ.put(msg)
    else:
      softLimitPQ = 0
  return None

# Update function-based fair share limits according to what functions
# we have seen so far
def updateFairShareFunctionQuota():
  psMetricServerLock.acquire()
  totalFunctions = 0
  uniqueFunctionList = []
  uniqueFunctionQuota = {}
  for i in metricServer.arrivalsChainsMetricList:
    totalFunctions = totalFunctions + len(i['chainFunctionIdList'])
    for j in i['chainFunctionIdList']:
      if (j in uniqueFunctionList):
        uniqueFunctionQuota[j] = uniqueFunctionQuota[j] + 1
      else:
        uniqueFunctionList.append(j)
        uniqueFunctionQuota[j] = 1 
  psMetricServerLock.release()
  # compute %age quota
  for key in uniqueFunctionQuota:
    uniqueFunctionQuota[key] = uniqueFunctionQuota[key]/totalFunctions
  metricServer.functionQuotas = uniqueFunctionQuota

# Update reactive function-based fair share limits according to
# arrival rates of functions
def updateFairShareArrivalFunctionQuota():
  psMetricServerLock.acquire()
  totalFunctions = 0
  uniqueFunctionList = []
  uniqueFunctionQuota = {}
  for i in metricServer.arrivalsChainsMetricList:
    chainArrivalRate = 1
    if (i['arrivalRate'] != 0):
      chainArrivalRate = i['arrivalRate']
    totalFunctions = totalFunctions + len(i['chainFunctionIdList'])*chainArrivalRate
    for j in i['chainFunctionIdList']:
      if (j in uniqueFunctionList):
        uniqueFunctionQuota[j] = uniqueFunctionQuota[j] + 1 * chainArrivalRate
      else:
        uniqueFunctionList.append(j)
        uniqueFunctionQuota[j] = 1 * chainArrivalRate
  psMetricServerLock.release()
  # compute %age quota
  for key in uniqueFunctionQuota:
    uniqueFunctionQuota[key] = uniqueFunctionQuota[key]/totalFunctions
  metricServer.functionQuotas = uniqueFunctionQuota

# Returns a list of functions that fully saturate their respective
# concurrency limits.
def getCandidateFunctionsAlreadyUsedQuota():
  candidateList = []
  functionQuotas = metricServer.functionQuotas
  for i in metricServer.getUniqueFunctionsList():
    psMetricServerLock.acquire()
    #print(i['functionId'],i['instancesRunning'],round(concurrency*functionQuotas[int(i['functionId'])]))
    if (i['instancesRunning'] >= round(concurrency*functionQuotas[int(i['functionId'])])):
    #if (i['functionsRunning'] >= 1):
      candidateList.append(i['functionId'])
    psMetricServerLock.release()
  return candidateList


previousPriorityList = []

# Strict Function Priority Policy:
# Functions are assigned priorities and higher priority functions
# are always served first
def strictFunctionPriorityPolicy():
  global previousPriorityList
  time.sleep(inMemorySleep)
  softLimitCRQ = kafkaCRQSoftLimit
  softLimitPQ = kafkaPQSoftLimit
  priorityList = metricServer.functionPrioritiesList
  choice = None
  choice_msg = ""
  while(softLimitCRQ > 0):
    if not(inMemoryCRQ.empty()):
      msg = inMemoryCRQ.get()
      chain = inMemory_to_chain_state(msg)
      softLimitCRQ = softLimitCRQ - 1
      if (chain.currentNode.function.id in priorityList):
        if (choice == None):
          choice = chain
          choice_msg = msg
        elif (priorityList.index(choice.currentNode.function.id)> priorityList.index(chain.currentNode.function.id)):
          inMemoryCRQ.put(choice_msg)
          choice = chain
          choice_msg = msg
        else:
          inMemoryCRQ.put(msg)
        if (priorityList.index(choice.currentNode.function.id) == 0):
          return choice
      else:
        inMemoryCRQ.put(msg)
    else:
      softLimitCRQ = 0
  while(softLimitPQ > 0):
    if not(inMemoryPQ.empty()):
      msg = inMemoryPQ.get()
      chain = inMemory_to_chain_state(msg)
      softLimitPQ = softLimitPQ - 1
      if (chain.currentNode.function.id in priorityList):
        if (choice == None):
          choice = chain
          choice_msg = msg
        elif (priorityList.index(choice.currentNode.function.id)> priorityList.index(chain.currentNode.function.id)):
          inMemoryPQ.put(choice_msg)
          choice = chain
          choice_msg = msg
        else:
          inMemoryPQ.put(msg)
        if (priorityList.index(choice.currentNode.function.id) == 0):
          return choice
      else:
        inMemoryPQ.put(msg)
    else:
      softLimitPQ = 0
  return choice

# Hybrid Bin Packing Policy:
# Invoke functions on a local/private cloud, then fall back to
# a public cloud if the local cloud is at full capacity
def hybridBinPackingPolicy():
  time.sleep(inMemorySleep)
  if not(inMemoryCRQ.empty()):
    msg = inMemoryCRQ.get()
    chain = inMemory_to_chain_state(msg)
    if (localCloudConcurrency._value < 1):
      chain.flags["hybrid"] = "remote"
    else:
      chain.flags["hybrid"] = "local"
    return chain
  else:
    if not(inMemoryPQ.empty()):
      chain = inMemory_to_chain_state(inMemoryPQ.get())
      if (localCloudConcurrency._value < 1):
        chain.flags["hybrid"] = "remote"
      else:
        chain.flags["hybrid"] = "local"
      return chain
    else:
      return None

# Simple Queue Priority Policy:
# Function level first come first serve, but we prioritize functions
# from the High Priority queue over the Low Priority queue
def simpleQueuePriorityPolicy():
  if not(inMemoryHighPriorityQueue.empty()):
    msg = inMemoryHighPriorityQueue.get()
    chain = inMemory_to_chain_state(msg)
    return chain
  else:
    if not(inMemoryLowPriorityQueue.empty()):
      chain = inMemory_to_chain_state(inMemoryLowPriorityQueue.get())
      return chain
    else:
      return None


# instantiating MetricServer
metricServer = MetricServer()
previousState = []

# setup kafka
kafka_url = "localhost:9092"
kafka_pq_topic = "pending_queue"
#print('Kafka setup for PQ ...')
producer_PQ = connect_kafka_producer(kafka_url)
consumer_PQ = KafkaConsumer(kafka_pq_topic, 
                         auto_offset_reset='latest',
                         bootstrap_servers=[kafka_url], 
                         api_version=(0, 10), 
                         consumer_timeout_ms=10000000)
#print('Kafka setup for CRQ ...')
kafka_crq_topic = "chain_running_queue"
producer_CRQ = connect_kafka_producer(kafka_url)
consumer_CRQ = KafkaConsumer(kafka_crq_topic, 
                         auto_offset_reset='latest',
                         bootstrap_servers=[kafka_url], 
                         api_version=(0, 10), 
                         consumer_timeout_ms=10000000)
#print('Kafka setup for FSide-logging ..')
kafka_fsq_topic = "function_side_logging_queue"
producer_FSQ = connect_kafka_producer(kafka_url)
consumer_FSQ = KafkaConsumer(kafka_fsq_topic, 
                         auto_offset_reset='latest',
                         bootstrap_servers=[kafka_url], 
                         api_version=(0, 10), 
                         consumer_timeout_ms=10000000)
#print('Kafka setup for CSide logging ..')
kafka_csq_topic = "consumer_side_logging_queue"
producer_CSQ = connect_kafka_producer(kafka_url)
consumer_CSQ = KafkaConsumer(kafka_csq_topic, 
                         auto_offset_reset='latest',
                         bootstrap_servers=[kafka_url], 
                         api_version=(0, 10), 
                         consumer_timeout_ms=10000000)
#print('Kafka setup for PSide logging ..')
kafka_psq_topic = "producer_side_logging_queue"
producer_PSQ = connect_kafka_producer(kafka_url)
consumer_PSQ = KafkaConsumer(kafka_psq_topic, 
                         auto_offset_reset='latest',
                         bootstrap_servers=[kafka_url], 
                         api_version=(0, 10), 
                         consumer_timeout_ms=10000000)
#print('Kafka setup for CSide logging ..')
kafka_csl_topic = "consumer_side_logging"
producer_CSL = connect_kafka_producer(kafka_url)
consumer_CSL = KafkaConsumer(kafka_csl_topic, 
                         auto_offset_reset='latest',
                         bootstrap_servers=[kafka_url], 
                         api_version=(0, 10), 
                         consumer_timeout_ms=10000000)

## in memory queue
inMemoryPQ = queue.Queue(maxsize=queueSize)
inMemoryCRQ = queue.Queue(maxsize=queueSize)
inMemoryFSQ = queue.Queue(maxsize=queueSize)
inMemoryCSQ = queue.Queue(maxsize=queueSize)
inMemoryCSSQ = queue.Queue(maxsize=queueSize)
inMemoryCSEQ = queue.Queue(maxsize=queueSize)
inMemoryPSQ = queue.Queue(maxsize=queueSize)
inMemoryCSL = queue.Queue(maxsize=queueSize)

# Only needed for the simple queue priority policy
inMemoryHighPriorityQueue = queue.Queue(maxsize=queueSize)
inMemoryLowPriorityQueue = queue.Queue(maxsize=queueSize)

# starting various threads
# kafka to in-memory PQ
threading.Thread(target=kafkaToInMemoryPQ).start()
# kafka to in-memory PSQ
threading.Thread(target=kafkaToInMemoryPSQ).start()
#print("Starting Logging Server")
threading.Thread(target=fsLogging).start()
#print("Starting Function Side metric-server")
threading.Thread(target=fsMetricServer).start()
#print("Starting Consumer Side metric-server")
threading.Thread(target=csMetricServer).start()
#print("Starting Producer Side metric-server")
threading.Thread(target=psMetricServer).start()
#print("Starting Consumer Side logger")
threading.Thread(target=csLogging).start()

# Start scheduling function invocations
schedule_invocations()
