# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponseRedirect
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import PictureForm
import boto3
import S3Utils
import os

def index(request):
	template = loader.get_template('index.html')
	return HttpResponse(template.render())

def event(request, id):
	template = loader.get_template('event.html')
	context = {}
	context['id'] = id
	print(request.method == 'POST')
	print(request.method)
	if request.method == 'POST':
		form = PictureForm(request.POST, request.FILES)
		if form.is_valid():
			print('uploading to s3...')
			handle_uploaded_file('upload/' + str(id) + '/', request.FILES['file'], 'upload/' + str(id) + '/' + request.FILES['file'].name)
			S3Utils.addPicture('upload/' + str(id) + '/' + request.FILES['file'].name)
			print('uploaded to s3')
		return render_to_response('event.html', context, context_instance=RequestContext(request))
	else:
		form = PictureForm()
		context['form'] = form
		return render_to_response('event.html', context, context_instance=RequestContext(request))

def handle_uploaded_file(folder, file, filename):
	if not os.path.exists(folder):
		os.mkdir(folder)

	with open(filename, 'wb+') as destination:
		for chunk in file.chunks():
			destination.write(chunk)