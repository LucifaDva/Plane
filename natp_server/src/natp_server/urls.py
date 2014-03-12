#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
from django.contrib import admin
admin.autodiscover()
import views, authorize, search, kml
from django.views.decorators.cache import cache_page
import django
import settings

urlpatterns = patterns('',
    url(r'^static/(?P<path>.*)$',django.views.static.serve,{'document_root':settings.STATIC_ROOT}),
    # Examples:
    # url(r'^$', 'natp_server.views.home', name='home'),
    # url(r'^natp_server/', include('natp_server.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$',authorize.login),
    url(r'^accounts/logout/$', authorize.logout),
    url(r'^$',views.index),
    url(r'^natp_server/$', views.index),
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^add_probe/$',views.add_probe),

    url(r'^report/$', views.update_from_report),
    
    
    url(r'^show/info/$', views.show_info),
    url(r'^show/all/$', views.show_all),
    url(r'^show/probe/$', views.show_probe),
    
    url(r'^kml/$', kml.output_kml),
    url(r'^kml/cancel/$', kml.cancel_task),
    url(r'^kml/readkml/$', kml.read_from_url),
    url(r'^kml/readimg/$', kml.read_img),
    
    url(r'^search/ident/$', search.search),
    url(r'^search/probe/$', search.search_probe),
    
  
)
