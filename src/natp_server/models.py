from django.db import models
from datetime import datetime

class Position(models.Model):
    icao = models.IntegerField()
    seen = models.CharField(max_length=60)
    alt = models.IntegerField()
    lat = models.FloatField(blank=True)
    lon = models.FloatField()
    probe = models.ForeignKey('Probe')
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    updated = models.DateTimeField(auto_now=True, default=datetime.now())
    #
    def __unicode__(self):
        return u'%s' % self.icao
    

class Vector(models.Model):
    icao = models.IntegerField()
    seen = models.CharField(max_length=60)
    speed = models.FloatField()
    heading = models.FloatField()
    vertical = models.FloatField()
    probe = models.ForeignKey('Probe')
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    updated = models.DateTimeField(auto_now=True, default=datetime.now())
    #
    def __unicode__(self):
        return ''
        

class Ident(models.Model):
    icao = models.IntegerField()
    ident = models.CharField(max_length=30)
    probe = models.ForeignKey('Probe')
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    updated = models.DateTimeField(auto_now=True, default=datetime.now())
    #
    def __unicode__(self):
        return u'%s: %d' %(self.ident, self.icao)
    
class Probe(models.Model):
    probe_name = models.CharField(max_length=60)
    province = models.CharField(max_length=60)   
    gps = models.CharField(max_length=60)
    #
    def __unicode__(self):
        return u'%s: %s' %(self.province, self.gps)

class Province(models.Model):
    province_id = models.IntegerField()
    province = models.CharField(max_length=60)

    def __unicode__(self):
        return '%s %s'%(self.province_id,self.province)


