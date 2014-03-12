#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from models import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from tasks import handle_xml
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import json
import memcache
from datetime import timedelta
from django.db import connection
from django.http import Http404

# 20
def sep_page(data,offset):
    paginator = Paginator(data,20)
    try:
        page = int(offset)
    except ValueError:
        page = 1
    try:
        contacts = paginator.page(page)
    except (EmptyPage,InvalidPage):
        contacts = paginator.page(paginator.num_pages)
    return contacts


@login_required
def show_all(request):
    """
    显示`id`的飞机信息
    """
    try:
        page = int(request.GET['page'])
    except:
        page = 1

    if 'ident' not in request.GET:
        raise Http404
    
    # ident表的id字段
    ident_id = request.GET['ident']
    ident = Ident.objects.get(id=ident_id)
    _icao = ident.icao
    _order = ident.order
    start_time = ident.created
    end_time = ident.updated
    
    if _order <= 1:
        ident_vectors = \
            Vector.objects.filter(icao=_icao).filter(seen__lte=end_time).order_by('-seen')
    else:
        ident_vectors = Vector.objects.filter(icao=_icao).filter(seen__gte=start_time).filter(seen__lte=end_time)
    
    page_vectors = sep_page(ident_vectors, page)
    
    for vector in page_vectors.object_list:
        """
        对每一个vector进行操作，找出时间最近的position信息
        1分钟内该飞机信息,拿出第一个
        （seen, seen+1)
        """
        seen = vector.seen
        end = vector.seen + timedelta(minutes=1)
        positions = Position.objects.filter(icao=_icao).filter(seen__gte=seen).filter(seen__lte=end)
        if not positions.exists():
            continue
        vector.position = positions[0]
    
    return render(request, 'show_all.html', {'page_vectors':page_vectors, 'ident':ident})


@login_required
def show_info(request):
    try:
        page = int(request.GET['page'])
    except:
        page = 1

    idents = Ident.objects.exclude(ident='').order_by('-updated')
    page_idents = sep_page(idents, page)
    
    for ident in page_idents.object_list:
        _icao = ident.icao
        _order = ident.order
        start_time = ident.created
        end_time = ident.updated
        
        if _order <= 1:
            ident_vectors = \
            Vector.objects.filter(icao=_icao).filter(seen__lte=end_time).order_by('-seen')
        else:
            ident_vectors = \
                Vector.objects.filter(icao=_icao).filter(seen__lte=end_time).filter(seen__gte=start_time).order_by('-seen')
        if not ident_vectors.exists():
            continue
        last_vector = ident_vectors[0]
        ident.detail = last_vector
        
    return render_to_response('show_info.html',{'icao_lst':page_idents},context_instance=RequestContext(request)) 


def update_from_report(request):
   
    data = request.body
    ip = request.META['REMOTE_ADDR']
    handle_xml.delay(data,ip)
    return HttpResponse('report ok')


@login_required
def index(request):
    return render_to_response('index.html',context_instance=RequestContext(request))


@login_required
def show_probe(request):
    
    try:
        page = request.GET['page']
    except KeyError:
        page = 1
        
    probes = Probe.objects.all()
    page_probes = sep_page(probes, page)
    
    return render(request, 'show_probe.html', {'page_probes':page_probes})


@login_required
def add_probe(request):
    errors = []
    provinces = Province.objects.all()

    if request.method == 'GET':
        return render(request, 'add_probe.html', {'provinces':provinces})
    
    
    prname = province = gps = ''
    try:
        prname = request.POST['prname']
        province = request.POST['province']
        gps = request.POST['gps']
    except KeyError:
        pass
    
    if not prname:
        errors.append('need a probe name!')
        return render(request, 'add_probe.html', {'provinces':provinces, 'errors':errors})
    
    try:
        province_object = Province.objects.get(province=province)
        
    except (Province.DoesNotExist, Province.MultipleObjectsReturned):
        errors.append('need a valid province!')
        return render(request, 'add_probe.html', {'provinces':provinces, 'errors':errors})
    
    Probe.objects.create(probe_name=prname, province=province_object,gps=gps)
    errors.append('add probe %s success.' % prname)
    
    return render(request, 'add_probe.html', {'provinces':provinces, 'errors':errors})


@login_required
def update(request):
    
    pass

def delete(request):
    
    pass

@login_required
def index(request):
    return render_to_response('index.html',context_instance=RequestContext(request))



