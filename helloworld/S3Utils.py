import boto3
import zipfile
import random
import string
import os

s3res = boto3.resource('s3')
s3cli = boto3.client('s3')
bucket = 'pictureeventjn'

def printBuckets():
	for bucket in s3.buckets.all():
		print(bucket.name)

def addPicture(filename):
	data = open(filename, 'rb')
	keys = []
	for a in s3res.Bucket('pictureeventjn').objects.all():
		if filename.rsplit('.', 1)[0] in a.key:
			keys.append(a.key)
	print(keys)
	if not filename in keys:
		s3res.Bucket(bucket).put_object(Key=filename, Body=data)
		print(filename + " uploaded")
		os.remove(filename)
		return
	count = 1
	filenamedbl = filename.rsplit('.', 1)[0] + '-' + str(count) + '.' + filename.rsplit('.', 1)[1]
	while filenamedbl in keys:
		count+=1
		filenamedbl = filename.rsplit('.', 1)[0] + '-' + str(count) + '.' + filename.rsplit('.', 1)[1]
	s3res.Bucket(bucket).put_object(Key=filenamedbl, Body=data)
	print(filenamedbl + " uploaded")
	os.remove(filename)


def listPictures(event_id):
	zf = zipfile.ZipFile('archive.zip', mode='w')
	try:
		for object in s3res.Bucket('pictureeventjn').objects.all():
			if object.key.split('/')[1] == event_id:
				print(object.key.split('/')[2])
				s3cli.download_file(bucket, object.key, 'tmp/' + object.key.split('/')[2])
				zf.write('tmp/' + object.key.split('/')[2])
	finally:
		zf.close()

def getArchive(event_id):
	rand = randomString(20)
	localpath = '/tmp/'+rand+'/archive.zip'
	os.makedirs('/tmp/'+rand+'/')
	response = s3cli.get_object(Bucket=bucket, Key='archives/' + event_id + '/archive.zip')
	s3cli.download_file(bucket, 'archives/' + event_id + '/archive.zip', localpath)
	return localpath

def addEmptyArch(remote, local):
	data = open(local, 'rb')
	s3res.Bucket(bucket).put_object(Key=remote, Body=data)
	
def randomString(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

