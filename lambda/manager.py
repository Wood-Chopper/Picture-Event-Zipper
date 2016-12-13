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

lastLambda = 0

print('Loading function')
sqscli = boto3.client('sqs')
sqsres = boto3.resource('sqs')
lambdacli = boto3.client('lambda')
cwecli = boto3.client('events')

bucket_lambda = 'np-7122f38739-lambda'
queuename = 'np-8f730ee7f5'
lambdaprefix = 'np-2f91b8ea89'
schedulename = 'np-1d51b1f2e6'

def get_last_Lambda():
    lambdasURL = lambdacli.list_functions()['Functions']
    
    max=0
    for function in lambdasURL:
        name = function['FunctionName']
        if lambdaprefix+'-' in name:
            print(name)
            spl = name.split('-')
            id = int(spl[len(spl)-1])
            if max < id:
                max = id
    print(max)
    return max

lastLambda=get_last_Lambda()

def lambda_handler(event, context):
    queue = sqsres.get_queue_by_name(QueueName=queuename)
    queueMessages = int(queue.attributes['ApproximateNumberOfMessages'])
    print('queueMessages = ' + str(queueMessages))
    if queueMessages > 200:
        print("Addind a node")
        addNode()
    elif queueMessages < 50 and lastLambda > 0:
        print("Removing a node")
        removeNode()
    
def addNode():
    global lastLambda
    lastLambda += 1
    exampleLambda = lambdacli.get_function(FunctionName=lambdaprefix)
    functionArn = lambdacli.create_function(
        FunctionName=lambdaprefix+'-'+str(lastLambda),
        Runtime='python2.7',
        Role=exampleLambda['Configuration']['Role'],
        Handler=exampleLambda['Configuration']['Handler'],
        Code={'S3Bucket': bucket_lambda, 'S3Key': 'zipper.zip'},
        Timeout=exampleLambda['Configuration']['Timeout'],
        MemorySize=exampleLambda['Configuration']['MemorySize']
    )['FunctionArn']
    ruleArn = cwecli.put_rule(
        Name=schedulename+'_' + str(lastLambda),
        ScheduleExpression='rate(1 minute)',
        State='ENABLED',
    )['RuleArn']
    cwecli.put_targets(
        Rule=schedulename+'_' + str(lastLambda),
        Targets=[
            {
                'Id': 'Invoke-' + str(lastLambda),
                'Arn': functionArn
            }
        ]
    )
    cwecli.enable_rule(Name=schedulename+'_' + str(lastLambda))
    lambdacli.add_permission(
        FunctionName=functionArn,
        StatementId='Trigger',
        Action='lambda:*',
        Principal='*'#ruleArn
    )
    
def removeNode():
    global lastLambda
    lambdacli.delete_function(FunctionName=lambdaprefix+'-'+str(lastLambda))
    cwecli.remove_targets(Rule=schedulename+'_' + str(lastLambda), Ids=['Invoke-' + str(lastLambda)])
    cwecli.delete_rule(Name=schedulename+'_' + str(lastLambda))
    lastLambda -= 1

        