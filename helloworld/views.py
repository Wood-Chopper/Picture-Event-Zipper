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
	print(request.method == 'POST')
	print(request.method)
	if request.method == 'POST':
		form = PictureForm(request.POST, request.FILES)
		if form.is_valid():
			### A mettre dans un thread
			#handle_uploaded_file('upload/' + str(id) + '/', request.FILES['file'], 'upload/' + str(id) + '/' + request.FILES['file'].name, request.FILES['file'].name)
			threading.Thread(target=handle_uploaded_file, args=['upload/' + str(id) + '/', request.FILES['file'], 'upload/' + str(id) + '/' + request.FILES['file'].name, request.FILES['file'].name]).start()
			###
			context['filename'] = request.FILES['file'].name
			
		form = PictureForm()
		context['form'] = form
		#S3Utils.listPictures(id)
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

def handle_uploaded_file(folder, file, filepath, filename):
	if not os.path.exists(folder):
		os.mkdir(folder)

	spl = filename.split('.')
	ext = spl[len(spl)-1]

	if ext == 'zip':
		with open(filepath, 'wb+') as destination:
			for chunk in file.chunks():
				destination.write(chunk)

		fh = open(filepath, 'rb')
		z = zipfile.ZipFile(fh)
		for name in z.namelist():
			if not '/' in name:
				outpath = folder
				z.extract(name, outpath)
				S3Utils.addPicture(folder + name)
		fh.close()
		return

	write_file(filepath, file)

	S3Utils.addPicture(filepath)

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





