import boto3
import zipfile
import random
import string
import os
from subprocess import call
from collections import defaultdict

s3res = boto3.resource('s3')
s3cli = boto3.client('s3')
bucket = 'pictureeventjn'

uploaded = defaultdict(lambda: 0)

locker = True

def printBuckets():
	for bucket in s3.buckets.all():
		print(bucket.name)

def addPicture(localPath):
	call(["convert", localPath, "-resize", "2000x2000>", localPath])
	data = open(localPath, 'rb')
	init_filename = localPath
	localPath = localPath.replace(' ', '_')
	split_part = localPath.split('/')
	new_key = split_part[0] + '/' + split_part[1] + '/' + split_part[3]
	keys = []
	for a in s3res.Bucket(bucket).objects.all():
		if new_key.rsplit('.', 1)[0] in a.key:
			keys.append(a.key)
	wait()
	lock()
	if not (new_key in keys) and (uploaded[new_key] == 0):
		uploaded[new_key] = 1
		unlock()
		try:
			s3res.Bucket(bucket).put_object(Key=new_key, Body=data)
		except:
			unlock()
			print("ERREUR LORS DE L'UPLOAD")
			print("Le fichier sera upload lors du prochain reboot")
			raise
			return
		print(new_key + " uploaded")
		os.remove(init_filename)
		return

	count = 1
	filenamedbl = new_key.rsplit('.', 1)[0] + '-' + str(count) + '.' + new_key.rsplit('.', 1)[1]
	while (filenamedbl in keys) | (uploaded[filenamedbl] == 1):
		count+=1
		filenamedbl = new_key.rsplit('.', 1)[0] + '-' + str(count) + '.' + new_key.rsplit('.', 1)[1]
	try:
		uploaded[filenamedbl] == 1
		s3res.Bucket(bucket).put_object(Key=filenamedbl, Body=data)
	except:
		print("ERREUR LORS DE L'UPLOAD")
		print("Le fichier sera upload lors du prochain reboot")
		raise
		return
	print(filenamedbl + " uploaded")
	os.remove(init_filename)

def addPictures(list):
	for file in list:
		addPicture(file)

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
	os.remove(local)
	
def randomString(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))


def wait():
	while locker == False:
		pass

def lock():
	locker = False

def unlock():
	locker = True

