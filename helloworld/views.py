# -*- coding: utf-8 -*-
from django.http import HttpResponse

def index(request):
	template = loader.get_template('index.html')
	return HttpResponse("Hello, world!")
