# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponseRedirect
from django import forms
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from forms import PictureForm
from django.http import StreamingHttpResponse
import boto3
import S3Utils
import os
import random
import string
import zipfile
import threading
from subprocess import call

def index(request):
	if request.method == 'POST':
		event_id = get_link()
		return redirect('/event/'+event_id)
	else:
		return render_to_response('index.html', context_instance=RequestContext(request))

def event(request, id):
	if not exist(id):
		return redirect('/')
	template = loader.get_template('event.html')
	context = {}
	context['id'] = id
	if request.method == 'POST':
		form = PictureForm(request.POST, request.FILES)
		if form.is_valid():
			handle_uploaded_file('upload/' + str(id) + '/',request.FILES['file'], request.FILES['file'].name)
			context['filename'] = request.FILES['file'].name
			
		form = PictureForm()
		context['form'] = form
		return render_to_response('event.html', context, context_instance=RequestContext(request))
	else:
		form = PictureForm()
		context['form'] = form
		return render_to_response('event.html', context, context_instance=RequestContext(request))

def archive(request, id):
	print('archive')
	localpath = S3Utils.getArchive(id)

	response = StreamingHttpResponse((line for line in open(localpath,'r')))
	response['Content-Disposition'] = "attachment; filename=Archive.zip"
	response['Content-Length'] = os.path.getsize(localpath)
	return response

def handle_uploaded_file(folder, file, filename):
	randFolder = randomString(20) + '/'
	localTempPath = folder + randFolder + filename
	filepath = folder + filename
	pictures = []

	if not os.path.exists(folder + randFolder):
		os.makedirs(folder + randFolder)

	spl = filename.split('.')
	ext = spl[len(spl)-1]

	if ext == 'zip':
		destination = open(localTempPath, 'wb+')
		for chunk in file.chunks():
			destination.write(chunk)
		destination.close()

		fh = open(localTempPath, 'rb')
		z = zipfile.ZipFile(fh)
		for name in z.namelist():
			if not '/' in name:
				outpath = folder + randFolder
				z.extract(name, outpath)
				pictures.append(folder + randFolder + name)
		fh.close()
		print("Zip extracted")
		os.remove(localTempPath)
	else:
		write_file(localTempPath, file)
		pictures.append(localTempPath)

	threading.Thread(target=S3Utils.addPictures, args=[pictures]).start()
	#S3Utils.addPictures(pictures)

def write_file(path, file):
	with open(path, 'wb+') as destination:
		for chunk in file.chunks():
			destination.write(chunk)

def get_link():
	random = randomString(20)
	if not os.path.exists('upload/'+random+'/'):
		os.makedirs('upload/'+random+'/')
		rd = '/tmp/' + randomString(20) + '/'
		os.makedirs(rd)
		zf = zipfile.ZipFile(rd + 'archive.zip', mode='w')
		zf.close()
		S3Utils.addEmptyArch('archives/'+random+'/archive.zip', rd + 'archive.zip')
		return random
	else:
		return get_link()

def randomString(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

def exist(id):
	return os.path.exists('upload/'+id+'/')

def test1(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = 'pictureeventjn'
	bucketArch = 'pictureeventarchivejn'

	data = open("test.jpg", 'rb')
	s3res.Bucket(bucket).put_object(Key="test/test.jpg", Body=data)

	context = {}
	context['pass'] = "put object to pictureeventjn OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))


def test2(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = 'pictureeventjn'
	bucketArch = 'pictureeventarchivejn'

	s3cli.download_file(bucket, "test/test.jpg", '/tmp/to_delete.jpg')

	context = {}
	context['pass'] = "get object from pictureeventjn OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))


def test3(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = 'pictureeventjn'
	bucketArch = 'pictureeventarchivejn'

	s3res.Bucket(bucket).objects.all()

	context = {}
	context['pass'] = "list objects from pictureeventjn OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))



def test1bis(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = 'pictureeventjn'
	bucketArch = 'pictureeventarchivejn'

	data = open("test.jpg", 'rb')
	s3res.Bucket(bucketArch).put_object(Key="test/test.jpg", Body=data)

	context = {}
	context['pass'] = "put object to pictureeventarchivejn OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))


def test2bis(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = 'pictureeventjn'
	bucketArch = 'pictureeventarchivejn'

	s3cli.download_file(bucketArch, "test/test.jpg", '/tmp/to_delete.jpg')

	context = {}
	context['pass'] = "get object from pictureeventarchivejn OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))


def test3bis(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = 'pictureeventjn'
	bucketArch = 'pictureeventarchivejn'

	s3res.Bucket(bucketArch).objects.all()

	context = {}
	context['pass'] = "list objects from pictureeventarchivejn OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))

def testImg(request):
	call(["convert", "test.jpg", "-resize", "2000x2000>", "test.jpg"])

	context = {}
	context['pass'] = "convert OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))




