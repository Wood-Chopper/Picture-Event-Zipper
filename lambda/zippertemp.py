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
from subprocess import call
from collections import defaultdict

SQS= [[QUEUE]]
bucket = [[BUCKET_IMAGES]]
bucketArch = [[BUCKET_ARCHIVES]]

print('Loading function')
sqscli = boto3.client('sqs')
sqsres = boto3.resource('sqs')
queue = sqsres.get_queue_by_name(QueueName=SQS)

s3res = boto3.resource('s3')
s3cli = boto3.client('s3')


def lambda_handler(event, context):
    print_disk_info()
    clear_tmp()

    messages = queue.receive_messages(MaxNumberOfMessages=1)
    sizetot = get_size(messages)
    pull_again=True
    while pull_again:
        temp = queue.receive_messages(MaxNumberOfMessages=1)
        if get_size(temp)+sizetot < 100000000 and len(messages)+1<=50 and len(messages)>0 :
            messages+=temp
            sizetot += get_size(temp)
        else:
            pull_again=False
            if len(temp) == 1:
                temp[0].change_visibility(VisibilityTimeout=0)

    print("size " + str(sizetot))
    print(str(len(messages)) + " pulled")
    listEventUpdated = []
    listKeys = []
    listMessages = []
    eventSizes = defaultdict(lambda: 0)
    for message in messages:
        parsed = json.loads(message.body)
        if 'Records' in parsed:
            key = parsed['Records'][0]['s3']['object']['key']
            addFileToArch(message, key, listEventUpdated, listKeys, listMessages)
            eventSizes[key.split('/')[1]]+=parsed['Records'][0]['s3']['object']['size']
        else:
            message.delete()
    sendArchive(listEventUpdated, listKeys, listMessages, eventSizes)
    return None
    
def get_size(messages):
    size = 0
    for message in messages:
        parsed = json.loads(message.body)
        if 'Records' in parsed:
            size += parsed['Records'][0]['s3']['object']['size']
    return size

def addFileToArch(message, key, listEvent, listKeys, listMessages):
    event_name = key.split('/')[1]
    if not event_name in listEvent:
        listEvent.append(event_name)
        listKeys.append([])
        listMessages.append([])
    indexEvent = listEvent.index(event_name)
    listKeys[indexEvent].append(key)
    listMessages[indexEvent].append(message)
    
def sendArchive(listEventUpdated, listKeys, listMessages, eventSizes):
        
    for i in range (0, len(listEventUpdated)):
        event = listEventUpdated[i]
        rd=randomString(20)
        os.makedirs('/tmp/'+rd)
        archivename = get_archive_name(event, eventSizes[event])
        print('downloading : archives/'+event+'/' + archivename)
        s3cli.download_file(bucketArch, 'archives/'+event+'/' + archivename, '/tmp/'+rd+'/' + archivename)
        chks = md5('/tmp/'+rd+'/' + archivename)
        zipper = zipfile.ZipFile('/tmp/'+rd+'/' + archivename, mode='a')
        for key in listKeys[i]:
            spl = key.split('.')
            ext = spl[len(spl)-1]
            if ext == 'zip':
                tempPath = '/tmp/'+rd+'/'+key.split('/')[2]
                print("downloading : " + key)
                s3cli.download_file(bucket, key, tempPath)
                fh = open(tempPath, 'rb')
                z = zipfile.ZipFile(fh)
                for name in z.namelist():
                    print('1')
                    outpath = '/tmp/'+rd+'/'+name
                    z.extract(name, '/tmp/'+rd+'/')
                    zipManageDouble(zipper, outpath, name)
                    os.remove(outpath)
                z.close()
            else:
                tempPath = '/tmp/'+rd+'/'+key.split('/')[2]
                print("downloading : " + key)
                s3cli.download_file(bucket, key, tempPath)
                zipManageDouble(zipper, tempPath, key.split('/')[2])
            os.remove(tempPath)
        zipper.close()
        
        if chks == s3cli.head_object(Bucket=bucketArch,Key='archives/'+event + '/' + archivename)['ETag'][1:-1]:
            data = open('/tmp/'+rd+'/' + archivename, 'rb')
            s3res.Bucket(bucketArch).put_object(Key='archives/'+event + '/' + archivename, Body=data)
            os.remove('/tmp/'+rd+'/' + archivename)
            for message in listMessages[i]:
                result = message.delete()
                print("Deleting message : " + str(result))
        else:
            print("Overlapping error")
            for message in listMessages[i]:
                message.change_visibility(VisibilityTimeout=0)

def zipManageDouble(zipper, path, name):
    count = 0
    tempName = name
    while tempName in zipper.namelist():
        count+=1
        tempName = name.rsplit('.', 1)[0] + '-' + str(count) + name.rsplit('.', 1)[1]
    #call(["convert", path, "-resize", "2000x2000>", path])
    zipper.write(path, tempName)
        
def get_archive_name(event, sizeToAdd):
    found = False
    i=0
    while not found:
        i+=1
        if not exists(bucketArch, 'archives/'+event + '/archive-' + str(i) + '.zip'):
            found = True
    filename = 'archive-' + str(i-1) + '.zip'
    obj = s3res.ObjectSummary(bucketArch, 'archives/'+event + '/' + filename)
    size = obj.size;
    if size + sizeToAdd > 500000000:
        filename = 'archive-'+str(i)+'.zip'
        rd = '/tmp/' + randomString(20) + '/'
        os.makedirs(rd)
        zf = zipfile.ZipFile(rd + filename, mode='w')
        zf.close()
        data = open(rd + filename, 'rb')
        s3res.Bucket(bucketArch).put_object(Key='archives/'+event + '/' + filename, Body=data)
        os.remove(rd + filename)
    return filename
    
    
def exists(bucket, key):
    for obj in s3res.Bucket(bucket).objects.all():
        if key == obj.key:
            return True
    return False
        
def randomString(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))
    
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def print_disk_info():
    f = os.statvfs("/tmp")
    print ("preferred block size => " + str(f[statvfs.F_BSIZE]))
    print ("fundamental block size => " + str(f[statvfs.F_FRSIZE]))
    print ("total blocks => " + str(f[statvfs.F_BLOCKS]))
    print ("total free blocks => " + str(f[statvfs.F_BFREE]))
    print ("available blocks => " + str(f[statvfs.F_BAVAIL]))
    print ("total file nodes => " + str(f[statvfs.F_FILES]))
    print ("total free nodes => " + str(f[statvfs.F_FFREE]))
    print ("available nodes => " + str(f[statvfs.F_FAVAIL]))
    print ("max file name length => " + str(f[statvfs.F_NAMEMAX]))
    
def clear_tmp():
    folder = '/tmp'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)