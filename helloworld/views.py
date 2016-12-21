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
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from shutil import copyfile
from shutil import rmtree
import imghdr
import sys
from subprocess import call

@csrf_exempt
def index(request):
	context = {}
	context['url_static'] = settings.URL_STATIC
	context['url_archives'] = settings.URL_ARCHIVES
	context['region'] = settings.REGION
	context['static'] = settings.BUCKET_STATIC
	if request.method == 'POST':
		event_id = get_link()
		return redirect('/event/'+event_id)
	else:
		return render_to_response('index.html', context, context_instance=RequestContext(request))

@csrf_exempt
def event(request, id):
	if not exist(id):
		return redirect('/')
	template = loader.get_template('event.html')
	context = {}
	context['id'] = id
	context['archives'] = S3Utils.get_available_archives(id)
	context['region'] = settings.REGION
	context['static'] = settings.BUCKET_STATIC
	context['bucket_archives'] = settings.BUCKET_ARCHIVES
	context['url_static'] = settings.URL_STATIC
	context['url_archives'] = settings.URL_ARCHIVES
	if request.method == 'POST':
		form = PictureForm(request.POST, request.FILES)
		if form.is_valid():
			context['filenames'], context['errors'] = handle_uploaded_file(id, 'upload/' + str(id) + '/',request.FILES['file'], request.FILES['file'].name)
			
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

def handle_uploaded_file(event, folder, file, filename):
	randFolder = randomString(20) + '/'
	localTempPath = folder + randFolder + filename
	filepath = folder + filename
	pictures = []
	returned = []
	error = []

	if not os.path.exists(folder + randFolder):
		os.makedirs(folder + randFolder)

	spl = filename.split('.')
	ext = spl[len(spl)-1]
	size = os.path.getsize(localTempPath)

	if size > 100000000:
		error.append(filename + ' is too big ('+ size/1000 +' KB)')
		os.remove(localTempPath)
		return returned, error
	elif ext == 'zip':
		destination = open(localTempPath, 'wb+')
		for chunk in file.chunks():
			destination.write(chunk)
		destination.close()
		if zip_error(localTempPath):
			error.append(filename + ' is not a valid zip file')
			os.remove(localTempPath)
			return returned, error

		fh = open(localTempPath, 'rb')
		z = zipfile.ZipFile(fh)
		newzippath = folder + randFolder + randomString(20) + '.zip'
		newzip = zipfile.ZipFile(newzippath, mode='w')
		for name in z.namelist():
			if not '/' in name:
				outpath = folder + randFolder
				z.extract(name, outpath)
				if imghdr.what(outpath + name) == None:
					print(name + ' is not an image')
					error.append(name + ' is not an image')
					os.remove(outpath + name)
				else:
					#call(["convert", outpath + name, "-resize", "2000x2000>", outpath + name])
					newzip.write(outpath + name, name)
					os.remove(outpath + name)
					returned.append(name)
			elif '__MACOSX' == name.split('/')[0]:
				pass
			elif '/' != name[-1]:
				outpath = folder + randFolder
				z.extract(name, outpath)
				src = outpath + name
				newname = name.replace('/', '_')
				dst = outpath + newname
				copyfile(src, dst)
				rmtree(folder + randFolder + name.split('/')[0])

				if imghdr.what(dst) == None:
					print(newname + ' is not an image')
					error.append(newname + ' is not an image')
					os.remove(dst)
				else:
					#call(["convert", dst, "-resize", "2000x2000>", dst])
					newzip.write(dst, newname)
					os.remove(dst)
					returned.append(newname)
		pictures.append(newzippath)
		newzip.close()
		fh.close()
		print("Zip extracted")
		os.remove(localTempPath)
		S3Utils.addPicture(pictures[0])
	else:
		write_file(localTempPath, file)
		if imghdr.what(localTempPath) == None:
			print(filename + ' is not an image')
			error.append(filename + ' is not an image')
			os.remove(localTempPath)
		else:
			#call(["convert", localTempPath, "-resize", "2000x2000>", localTempPath])
			pictures.append(localTempPath)
			returned = [filename]
		S3Utils.addPictures(event, pictures)

	return returned, error

def write_file(path, file):
	with open(path, 'wb+') as destination:
		for chunk in file.chunks():
			destination.write(chunk)

def zip_error(path):
	try:
		fh = open(path, 'rb')
		z = zipfile.ZipFile(fh)
		z.namelist()
		fh.close()
		return False
	except:
		print("Unexpected error:", sys.exc_info()[0])
		return True

def get_link():
	random = randomString(20)
	if not id in S3Utils.get_events_id():
		rd = '/tmp/' + randomString(20) + '/'
		os.makedirs(rd)
		zf = zipfile.ZipFile(rd + 'archive-1.zip', mode='w')
		zf.close()
		S3Utils.addEmptyArch('archives/'+random+'/archive-1.zip', rd + 'archive-1.zip')
		return random
	else:
		return get_link()

def randomString(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

def exist(id):
	return (id in S3Utils.get_events_id())

def test1(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = settings.BUCKET_IMAGES
	bucketArch = settings.BUCKET_ARCHIVES

	data = open("test.jpg", 'rb')
	s3res.Bucket(bucket).put_object(Key="test/test.jpg", Body=data)

	context = {}
	context['pass'] = "put object to img OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))


def test2(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = settings.BUCKET_IMAGES
	bucketArch = settings.BUCKET_ARCHIVES

	s3cli.download_file(bucket, "test/test.jpg", '/tmp/to_delete.jpg')

	context = {}
	context['pass'] = "get object from img OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))


def test3(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = settings.BUCKET_IMAGES
	bucketArch = settings.BUCKET_ARCHIVES

	s3res.Bucket(bucket).objects.all()

	context = {}
	context['pass'] = "list objects from img OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))



def test1bis(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = settings.BUCKET_IMAGES
	bucketArch = settings.BUCKET_ARCHIVES

	data = open("test.jpg", 'rb')
	s3res.Bucket(bucketArch).put_object(Key="test/test.jpg", Body=data)

	context = {}
	context['pass'] = "put object to arch OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))


def test2bis(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = settings.BUCKET_IMAGES
	bucketArch = settings.BUCKET_ARCHIVES

	s3cli.download_file(bucketArch, "test/test.jpg", '/tmp/to_delete.jpg')

	context = {}
	context['pass'] = "get object from arch OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))


def test3bis(request):
	s3res = boto3.resource('s3')
	s3cli = boto3.client('s3')
	bucket = settings.BUCKET_IMAGES
	bucketArch = settings.BUCKET_ARCHIVES

	s3res.Bucket(bucketArch).objects.all()

	context = {}
	context['pass'] = "list objects from arch OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))

def testImg(request):
	call(["convert", "test.jpg", "-resize", "2000x2000>", "test.jpg"])

	context = {}
	context['pass'] = "convert OK"
	return render_to_response('test.html', context, context_instance=RequestContext(request))




