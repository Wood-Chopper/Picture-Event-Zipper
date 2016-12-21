from __future__ import print_function

import json
import urllib
import boto3
import string
from collections import defaultdict
import time
import os
import random
import hashlib
import zipfile
from subprocess import call

print('Loading function')

s3res = boto3.resource('s3')
s3cli = boto3.client('s3')
bucket = [[BUCKET_IMAGES]]

def lambda_handler(event, context):
    rd = randomString(20)
    if 'Records' in event:
        key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
        tempPath = '/tmp/'+rd+'/'+key.split('/')[2]
        os.makedirs('/tmp/'+rd)
        s3cli.download_file(bucket, key, tempPath)
        id = key.split('/')[1]
        spl = key.split('.')
        ext = spl[len(spl)-1]
        if ext=='zip':
            fh = open(tempPath, 'rb')
            z = zipfile.ZipFile(fh)
            for name in z.namelist():
                outpath = '/tmp/'+rd+'/'+name
                z.extract(name, '/tmp/'+rd+'/')
                resize_send(outpath, name, id)
                os.remove(outpath)
            z.close()
        else:
            name = key.split('/')[2]
            resize_send(tempPath, name, id)
        os.remove(tempPath)
    return None

def resize_send(path, name, id):
    keys = []
    for a in s3res.Bucket(bucket).objects.all():
        keys.append(a.key)
    if not 'resized/'+id + '/' + name in keys:
        call(["convert", path, "-resize", "2000x2000>", path])
        data = open(path, 'rb')
        s3res.Bucket(bucket).put_object(Key='resized/'+id + '/' + name, Body=data)
        print(name + ' resized')

    
def exists(bucket, key):
    for obj in s3res.Bucket(bucket).objects.all():
        if key == obj.key:
            return True
    return False
        
def randomString(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))
