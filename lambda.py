from __future__ import print_function

import json
import urllib
import boto3
import zipfile
import os
import random
import shutil
import string

print('Loading function')

s3res = boto3.resource('s3')
s3cli = boto3.client('s3')
bucket = 'pictureeventjn'

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        response = s3cli.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'] + " " + key)
        event_id = key.split('/')[1]
        listPictures(event_id)
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
        
def randomString(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def listPictures(event_id):
    rand = randomString(20)
    rd = '/tmp/' + rand + '/'
    if not os.path.exists(rd):
        os.mkdir(rd)
    zf = zipfile.ZipFile(rd + 'archive.zip', mode='w')
    try:
        for object in s3res.Bucket(bucket).objects.all():
            if object.key.split('/')[1] == event_id and object.key.split('/')[0] == "upload":
                print(object.key.split('/')[2])
                s3cli.download_file(bucket, object.key, rd + object.key.split('/')[2])
                zf.write(rd + object.key.split('/')[2])
                print(object.key.split('/')[2] + " dans zip")
    finally:
        zf.close()
    data = open(rd + 'archive.zip', 'rb')
    s3res.Bucket(bucket).put_object(Key='archives/'+event_id + '/archive.zip', Body=data)
    shutil.rmtree('/tmp/' + rand)
    s3cli.get_object(Bucket=bucket, Key='archives/' + event_id + '/archive.zip').Acl().put(ACL='public-read')#A regler
    