from django.contrib import admin
from models import *

class ReportAdmin(admin.ModelAdmin):
    list_display = ('ip','count','probe','created')
    ordering = ('-created',)

class ProbeAdmin(admin.ModelAdmin):
    list_display = ('probe_name','province','gps')
    ordering = ('probe_name',)

class IdentAdmin(admin.ModelAdmin):
    list_display = ('icao','ident', 'order', 'valid', 'probe','created','updated')
    ordering = ('-updated',)

class VectorAdmin(admin.ModelAdmin):
    list_display = ('icao','seen','speed','heading','vertical','probe','created','updated')
    ordering = ('-updated',)

class PositionAdmin(admin.ModelAdmin):
    list_display = ('seen','alt','lat','lon','probe','created','updated')
    ordering = ('-updated',)

class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('province',)
    ordering = ('province',)

class UsersetAdmin(admin.ModelAdmin):
    list_display = ('username','password')
    ordering = ('username',)

admin.site.register(Report,ReportAdmin)
admin.site.register(Province,ProvinceAdmin)
admin.site.register(Position,PositionAdmin)
admin.site.register(Vector,VectorAdmin)
admin.site.register(Ident,IdentAdmin)
admin.site.register(Probe,ProbeAdmin)


