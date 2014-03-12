#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from datetime import datetime

class Report(models.Model):
    ip = models.IPAddressField()
    count = models.IntegerField()
    probe = models.ForeignKey('Probe')
    created = models.DateTimeField(auto_now_add=True,default=datetime.now())


class Position(models.Model):
    icao = models.IntegerField()
    seen = models.DateTimeField()
    alt = models.IntegerField()
    lat = models.FloatField(blank=True)
    lon = models.FloatField()
    probe = models.ForeignKey('Probe')
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    updated = models.DateTimeField(auto_now=True, default=datetime.now())
    
    #
    def __unicode__(self):
        return u'%s:(seen=%s)' % (self.icao, self.seen)
    

class Vector(models.Model):
    icao = models.IntegerField()
    seen = models.DateTimeField()
    speed = models.FloatField()
    heading = models.FloatField()
    vertical = models.FloatField()
    probe = models.ForeignKey('Probe')
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    updated = models.DateTimeField(auto_now=True, default=datetime.now())
    
    #
    def __unicode__(self):
        return u'%s:(seen=%s)' % (self.icao, self.seen)
        

class Ident(models.Model):
    icao = models.IntegerField()
    ident = models.CharField(max_length=30)
    probe = models.ForeignKey('Probe')
    order = models.IntegerField()
    valid = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    updated = models.DateTimeField(auto_now=True, default=datetime.now())
    
    #
    def __unicode__(self):
        return u'[%d - %s - %d]' % (self.icao, self.ident, self.order)
    
    
class Probe(models.Model):
    probe_name = models.CharField(max_length=60)
    province = models.ForeignKey('Province')
    gps = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    updated = models.DateTimeField(auto_now=True, default=datetime.now())
    
    #
    def __unicode__(self):
        return u'%s' % self.probe_name

class Province(models.Model):
    province = models.CharField(max_length=60)
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    updated = models.DateTimeField(auto_now=True, default=datetime.now())

    #
    def __unicode__(self):
        return u'%s' % self.province