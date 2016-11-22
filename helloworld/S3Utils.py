import boto3
import zipfile

s3res = boto3.resource('s3')
s3cli = boto3.client('s3')

def printBuckets():
	for bucket in s3.buckets.all():
		print(bucket.name)

def addPicture(filename):
	data = open(filename, 'rb')
	s3res.Bucket('pictureeventjn').put_object(Key=filename, Body=data)

def listPictures(event_id):
	zf = zipfile.ZipFile('archive.zip', mode='w')
	try:
		for object in s3res.Bucket('pictureeventjn').objects.all():
			if object.key.split('/')[1] == event_id:
				print(object.key.split('/')[2])
				s3cli.download_file('pictureeventjn', object.key, 'tmp/' + object.key.split('/')[2])
				zf.write('tmp/' + object.key.split('/')[2])
	finally:
		zf.close()
	

