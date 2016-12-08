from __future__ import print_function

import boto3
import json
import os
import zipfile
import random
import string
import shutil
import sys,os,statvfs
import hashlib

lastQueue = None

print('Loading function')
sqscli = boto3.client('sqs')
sqsres = boto3.resource('sqs')
lambdacli = boto3.client('lambda')
cwecli = boto3.client('events')

def get_last_SQS():
    queuesURL = sqscli.list_queues(QueueNamePrefix='s3toLambdaElastic')
    max=0
    for url in queuesURL['QueueUrls']:
        print(sqsres.Queue(url).attributes['QueueArn'])
        arn = sqsres.Queue(url).attributes['QueueArn']
        spl = arn.split('-')
        id = int(spl[len(spl)-1])
        if max < id:
            max = id
    print(id)
    return int(id)

lastSQS=get_last_SQS()

def lambda_handler(event, context):
    global LastSQS
    global lastQueue
    lastQueue = sqsres.get_queue_by_name(QueueName="s3toLambdaElastic-"+str(lastSQS))
    lastQueueMessages = int(lastQueue.attributes['ApproximateNumberOfMessages']) + int(lastQueue.attributes['ApproximateNumberOfMessagesNotVisible'])
    print('lastQueueMessages = ' + str(lastQueueMessages))
    if lastQueueMessages > 0:
        print("Addind a node")
        addNode()
        return None
    if lastSQS==1:
        return None
    secondLastQueue = sqsres.get_queue_by_name(QueueName='s3toLambdaElastic-'+str(lastSQS-1))
    secondLastQueueMessages = int(secondLastQueue.attributes['ApproximateNumberOfMessages']) + int(secondLastQueue.attributes['ApproximateNumberOfMessagesNotVisible'])
    if lastQueueMessages + secondLastQueueMessages == 0:
        print("Deleting a node")
        print("Removing a node")
        removeNode()
    
def addNode():
    global lastSQS
    sqscli.create_queue(QueueName="s3toLambdaElastic-" + str(lastSQS+1), Attributes={'VisibilityTimeout' : '60'})
    newQueue = sqsres.get_queue_by_name(QueueName="s3toLambdaElastic-"+str(lastSQS+1))
    policy = {
        "maxReceiveCount" : 1000,
        "deadLetterTargetArn": newQueue.attributes['QueueArn']
    }
    lastQueue.set_attributes(Attributes={'RedrivePolicy': json.dumps(policy)})
    lastSQS+=1
    exampleLambda = lambdacli.get_function(FunctionName='S3SQSZIP')
    functionArn = lambdacli.create_function(
        FunctionName='S3SQSZIP-'+str(lastSQS),
        Runtime='python2.7',
        Role=exampleLambda['Configuration']['Role'],
        Handler=exampleLambda['Configuration']['Handler'],
        Code={'S3Bucket': 'pictureeventressources', 'S3Key': 'Lambda.zip'},
        Timeout=60,
        MemorySize=512
    )['FunctionArn']
    ruleArn = cwecli.put_rule(
        Name='Schedule-' + str(lastSQS),
        ScheduleExpression='rate(1 minute)',
        State='ENABLED',
    )['RuleArn']
    cwecli.put_targets(
        Rule='Schedule-' + str(lastSQS),
        Targets=[
            {
                'Id': 'Invoke-' + str(lastSQS),
                'Arn': functionArn
            }
        ]
    )
    
def removeNode():
    global lastSQS
    lambdacli.delete_function(FunctionName='S3SQSZIP-'+str(lastSQS))
    cwecli.remove_targets(Rule='Schedule-' + str(lastSQS), Ids=['Invoke-' + str(lastSQS)])
    cwecli.delete_rule(Name='Schedule-' + str(lastSQS))
    sqsres.get_queue_by_name(QueueName="s3toLambdaElastic-"+str(lastSQS)).delete()
    lastSQS-=1

        