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

def get_last_Lambda():
    lambdasURL = lambdacli.list_functions()['Functions']
    
    max=0
    for function in lambdasURL:
        name = function['FunctionName']
        if 'S3SQSZIP-' in name:
            print(name)
            spl = name.split('-')
            id = int(spl[len(spl)-1])
            if max < id:
                max = id
    print(max)
    return max

lastLambda=get_last_Lambda()

def lambda_handler(event, context):
    queue = sqsres.get_queue_by_name(QueueName="s3tolambda")
    queueMessages = int(queue.attributes['ApproximateNumberOfMessages'])
    print('queueMessages = ' + str(queueMessages))
    if queueMessages > 200:
        print("Addind a node")
        addNode()
    elif queueMessages == 0 and lastLambda > 0:
        print("Removing a node")
        removeNode()
    
def addNode():
    global lastLambda
    lastLambda += 1
    exampleLambda = lambdacli.get_function(FunctionName='S3SQSZIP')
    functionArn = lambdacli.create_function(
        FunctionName='S3SQSZIP-'+str(lastLambda),
        Runtime='python2.7',
        Role=exampleLambda['Configuration']['Role'],
        Handler=exampleLambda['Configuration']['Handler'],
        Code={'S3Bucket': 'pictureeventressources', 'S3Key': 'Lambda.zip'},
        Timeout=exampleLambda['Configuration']['Timeout'],
        MemorySize=exampleLambda['Configuration']['MemorySize']
    )['FunctionArn']
    ruleArn = cwecli.put_rule(
        Name='Schedule_' + str(lastLambda),
        ScheduleExpression='rate(1 minute)',
        State='ENABLED',
    )['RuleArn']
    cwecli.put_targets(
        Rule='Schedule_' + str(lastLambda),
        Targets=[
            {
                'Id': 'Invoke-' + str(lastLambda),
                'Arn': functionArn
            }
        ]
    )
    cwecli.enable_rule(Name='Schedule_' + str(lastLambda))
    lambdacli.add_permission(
        FunctionName=functionArn,
        StatementId='Trigger',
        Action='lambda:*',
        Principal='*'#ruleArn
    )
    
def removeNode():
    global lastLambda
    lambdacli.delete_function(FunctionName='S3SQSZIP-'+str(lastLambda))
    cwecli.remove_targets(Rule='Schedule_' + str(lastLambda), Ids=['Invoke-' + str(lastLambda)])
    cwecli.delete_rule(Name='Schedule_' + str(lastLambda))
    lastLambda -= 1

        