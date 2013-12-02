from django.contrib import admin
from models import *


class ProbeAdmin(admin.ModelAdmin):
    list_display = ('probe_name','province','gps')
    ordering = ('probe_name',)

class IdentAdmin(admin.ModelAdmin):
    list_display = ('icao','ident','probe','created','updated')
    ordering = ('-updated',)

class VectorAdmin(admin.ModelAdmin):
    list_display = ('icao','seen','speed','heading','vertical','probe','created','updated')
    ordering = ('-updated',)

class PositionAdmin(admin.ModelAdmin):
    list_display = ('seen','alt','lat','lon','probe','created','updated')
    ordering = ('-updated',)

class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('province_id','province')
    ordering = ('province_id',)

class UsersetAdmin(admin.ModelAdmin):
    list_display = ('username','password')
    ordering = ('username',)


admin.site.register(Province,ProvinceAdmin)


admin.site.register(Position,PositionAdmin)
admin.site.register(Vector,VectorAdmin)
admin.site.register(Ident,IdentAdmin)
admin.site.register(Probe,ProbeAdmin)



