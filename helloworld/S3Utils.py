import boto3
import zipfile
import random
import string
import os
from subprocess import call

s3res = boto3.resource('s3')
s3cli = boto3.client('s3')
bucket = 'pictureeventjn'

def printBuckets():
	for bucket in s3.buckets.all():
		print(bucket.name)

def addPicture(filename):
	call(["convert", filename, "-resize", "2000x2000>", filename])
	data = open(filename, 'rb')
	init_filename = filename
	filename = filename.replace(' ', '_')
	keys = []
	for a in s3res.Bucket('pictureeventjn').objects.all():
		if filename.rsplit('.', 1)[0] in a.key:
			keys.append(a.key)
	if not filename in keys:
		try:
			s3res.Bucket(bucket).put_object(Key=filename, Body=data)
		except:
			print("ERREUR LORS DE L'UPLOAD")
			print("Le fichier sera upload lors du prochain reboot")
			raise
			return
		print(filename + " uploaded")
		os.remove(init_filename)
		return

	count = 1
	filenamedbl = filename.rsplit('.', 1)[0] + '-' + str(count) + '.' + filename.rsplit('.', 1)[1]
	while filenamedbl in keys:
		count+=1
		filenamedbl = filename.rsplit('.', 1)[0] + '-' + str(count) + '.' + filename.rsplit('.', 1)[1]
	try:
		s3res.Bucket(bucket).put_object(Key=filenamedbl, Body=data)
	except:
		print("ERREUR LORS DE L'UPLOAD")
		print("Le fichier sera upload lors du prochain reboot")
		raise
		return
	print(filenamedbl + " uploaded")
	os.remove(filename)

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
	
def randomString(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

