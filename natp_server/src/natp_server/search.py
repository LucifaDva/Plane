#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from models import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

import memcache
from util import _parse
from datetime import datetime, timedelta
from views import sep_page

@login_required
def search(request):
    errors = []
    ident_idents = Ident.objects.exclude(ident='').values_list('ident', flat=True).distinct().order_by('ident')
    
    if 'ident' not in request.GET:
        return render(request, 'search.html', {'idents':ident_idents})
    
    q_ident = request.GET['ident']
    idents = Ident.objects.filter(ident__icontains=q_ident)
    
    if not idents:
        errors.append('need a valid ident')
        return render(request, 'search.html', {'idents':ident_idents, 'errors':errors})
    
    try:
        page = request.GET['page']
    except KeyError:
        page = 1
    
    page_idents = sep_page(idents, page)
    
    "查询该ident航班的所有icao信息"
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
    return render(request, 'search_result.html', {'icao_lst':page_idents, 'ident':q_ident})


def search_probe(request):

    errors = []
    probe_name = ''
    
    try:
        page = request.REQUEST['page']
    except KeyError:
        page = 1
        
    try:
        probe_name = request.REQUEST['prname']
    except KeyError:
        pass
    
    try:
        probe_object = Probe.objects.get(probe_name__iexact=probe_name)
    except (Probe.DoesNotExist, Probe.MultipleObjectsReturned):
        errors.append('need a valid probe name')
        return render(request, 'show_info_with_probe.html', {'errors':errors})
    
    idents = Ident.objects.exclude(ident='').filter(probe=probe_object).order_by('-updated')
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
    
    return render(request, 'show_info_with_probe.html', {'errors':errors, 'probe_name':probe_name, 'page_idents':page_idents})
        
@login_required
def advanced_search(request):
   
    errors = []
    ident_idents = Ident.objects.exclude(ident='').values_list('ident', flat=True).distinct().order_by('ident')
    probe_names = Probe.objects.order_by('province')
    
    # get
    if request.method == 'GET' and 'ident' not in request.GET:
        return render(request, 'advance_search.html', {'errors': errors, 'ident_idents':ident_idents, 'probe_names':probe_names})
    else:
        # handle page
        pass
    
    
    # post
    
    q_ident = q_date = q_probe = ''

    if 'ident' in request.POST:
        q_ident = request.POST['ident']
    
    if 'date' in request.POST:
        q_date = request.POST['date']
        
    if 'probe' in request.POST:
        q_probe = request.POST['probe']
    
    request_type = int(bool(q_ident))*4 + int(bool(q_probe))*2 + int(bool(q_date))*1
    
    
    # 0
    if request_type == 0:
        errors.append('need one condition at least.')
        return render(request, 'advance_search.html', {'errors': errors, 'ident_idents':ident_idents, 'probe_names':probe_names})
    
    # 1 date
    if request_type == 1:
        pass
    
    # 2 probe
    if request_type == 2:
        probe_objects = Probe.objects.filter(probe_name=q_probe)
        probe_object = probe_objects[0]
        
        ident_objects = Ident.objects.filter(probe_)
        
    # 3 probe & date
    
    # 4 ident
    if reqeust_type == 4:
        pass
    
        
    # 必须填写ident
    if not ident:
        errors.append('请选择一个航班号进行查询')
        return render_to_response('advance_search.html',{'probes':probes,'idents':idents, 'errors': errors},context_instance=RequestContext(request)) 
        
    if 'seen' in request.POST:
        seen = request.POST['seen']

    if 'probe' in request.POST:
        pr = request.POST['probe']
        probe = Probe.objects.filter(probe_name=pr)
        if not probe:
            probe = ''
    
    vets = mc.get('mc_vectors')
    if vets:
        vectors = vets
    else:
        vectors = Vector.objects.all()
        mc.set('mc_vectors', vectors)
        
    filted_idents = idents.filter(ident=ident)
    ident_icaos = []
    for _ident in filted_idents:
        ident_icaos.append(_ident.icao)
        
    vectors = vectors.filter(icao__in=ident_icaos)
    
    if seen:
        vectors = vectors.filter(seen__startswith=seen)
    if probe:
        vectors = vectors.filter(probe=probe)
    
    vectors = vectors.order_by('-seen')
    date_list = []
    for d in vectors:
        d.ident = ident
        icao = d.icao
        
        # 为每一个vector寻找一个position, 误差在60s内
        stamp = _parse(d.seen)
        start = d.seen
        end = stamp + timedelta(seconds=60)
        
        position_60 = Position.objects.filter(icao=icao,probe=d.probe,seen__range=(start,end))
        if position_60:
            d.position = position_60[0]
        
        # date
        d.date = d.seen[:10]
        if d.date not in date_list:
            d.flag = 1
            date_list.append(d.date)
    
    return render_to_response('advance_search_result.html',{'ve':vectors},context_instance=RequestContext(request))