import boto3

s3 = boto3.resource('s3')

def printBuckets():
	for bucket in s3.buckets.all():
		print(bucket.name)

def addPicture(filename):
	data = open(filename, 'rb')
	s3.Bucket('pictureeventjn').put_object(Key=filename, Body=data)

def listPictures(event_id):
	for object in s3.Bucket('pictureeventjn').objects.all():
		if object.key.split('/')[1] == event_id:
			print(object.key.split('/')[2])
			boto3.client('s3').download_file('pictureeventjn', object.key, 'tmp/' + object.key.split('/')[2])
			open('tmp/' + object.key.split('/')[2]).read()

