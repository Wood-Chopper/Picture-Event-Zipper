# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponseRedirect
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext

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
		if 'pic' in request.FILES:
			context['filename'] = str(request.FILES['pic'])
			return render_to_response('event.html', context, context_instance=RequestContext(request))
	else:
		return render_to_response('event.html', context, context_instance=RequestContext(request))

def handle_uploaded_file(file, filename):
	if not os.path.exists('upload/'):
		os.mkdir('upload/')

	with open('upload/' + filename, 'wb+') as destination:
		for chunk in file.chunks():
			destination.write(chunk)