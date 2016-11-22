import boto3

s3 = boto3.resource('s3')

def printBuckets():
	for bucket in s3.buckets.all():
		print(bucket.name)

def addPicture(filename):
	data = open(filename, 'rb')
	s3.Bucket('pictureeventjn').put_object(Key=filename, Body=data)