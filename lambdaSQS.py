from __future__ import print_function

import boto3
import json
import os
import zipfile
import random
import string

print('Loading function')
sqscli = boto3.client('sqs')
sqsres = boto3.resource('sqs')
queue = sqsres.get_queue_by_name(QueueName='s3tolambda')

s3res = boto3.resource('s3')
s3cli = boto3.client('s3')
bucket = 'pictureeventjn'

#python-imaging
#ImageMagick en appel de commande

def lambda_handler(event, context):
    messages = queue.receive_messages(MaxNumberOfMessages=10)
    print(str(len(messages)) + " pulled")
    listEventUpdated = []
    listArchive = []
    listZippers = []
    for message in messages:
        parsed = json.loads(message.body)
        key = parsed['Records'][0]['s3']['object']['key']
        addFileToArch(key, listEventUpdated, listArchive, listZippers)
        result = message.delete()
        print("Deleting : " + str(result))
    sendArchive(listEventUpdated, listArchive, listZippers)
    return None

def addFileToArch(key, listEvent, listArchive, listZippers):
    event_name = key.split('/')[1]
    if not event_name in listEvent:
        rd=randomString(20)
        os.makedirs('/tmp/'+rd)
        listArchive.append(rd)
        listEvent.append(event_name)
        s3cli.download_file(bucket, 'archives/'+event_name+'/archive.zip', '/tmp/'+rd+'/archive.zip')
        listZippers.append(zipfile.ZipFile('/tmp/'+rd+'/archive.zip', mode='a'))
    indexEvent = listEvent.index(event_name)
    tempPath = '/tmp/'+listArchive[indexEvent]+'/'+key.split('/')[2]
    s3cli.download_file(bucket, key, tempPath)
    if not key.split('/')[2] in listZippers[indexEvent].namelist():
        listZippers[indexEvent].write(tempPath, key.split('/')[2])
    
def sendArchive(listEventUpdated, listArchive, listZippers):
    for i in range(len(listEventUpdated)):
        listZippers[i].close()
        data = open('/tmp/'+listArchive[i]+'/archive.zip', 'rb')
        s3res.Bucket(bucket).put_object(Key='archives/'+listEventUpdated[i] + '/archive.zip', Body=data)
    
        
def randomString(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))
