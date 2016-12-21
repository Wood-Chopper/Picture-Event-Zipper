# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include
from django.conf import settings
import os
import S3Utils
import threading

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()


urlpatterns = patterns('',

    # Uncomment the admin/doc line below to enable admin documentation:
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),

    (r'^test1/', 'helloworld.views.test1'),
    (r'^test2/', 'helloworld.views.test2'),
    (r'^test3/', 'helloworld.views.test3'),
    (r'^testimg/', 'helloworld.views.testImg'),

    (r'^test1bis/', 'helloworld.views.test1bis'),
    (r'^test2bis/', 'helloworld.views.test2bis'),
    (r'^test3bis/', 'helloworld.views.test3bis'),

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

