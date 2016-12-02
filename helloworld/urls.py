# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include
from django.conf import settings
import os
import S3Utils
import threading

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

def uploadOldFiles():
    events = os.listdir('upload')
    filesLeft = []
    for event in events:
        files = os.listdir('upload/' + event)
        for file in files:
            filesLeft.append('upload/' + event + '/' + file)
    print("files : " + str(filesLeft))
    for filename in filesLeft:
        S3Utils.addPicture(filename)

threading.Thread(target=uploadOldFiles).start()


urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^event/(?P<id>\w+)/', 'helloworld.views.event'),
    (r'^event/(?P<id>\w+)', 'helloworld.views.event'),

    (r'^archive/(?P<id>\w+)/', 'helloworld.views.archive'),
    (r'^archive/(?P<id>\w+)', 'helloworld.views.archive'),

    # Hello, world!
    (r'', 'helloworld.views.index'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )

