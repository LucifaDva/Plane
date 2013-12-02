from django.shortcuts import render
from django.http import HttpResponse
from models import *
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib import auth
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from util import get_data, handle_dict, update2db
from kml import genkml, write_to_xml
from django.core.servers.basehttp import FileWrapper
from django.core.paginator import Paginator, InvalidPage, EmptyPage

@login_required
def update_from_file(request):
    errors = []
    data = ""
    if 'filename' in request.FILES:
        _file = request.FILES['filename']
        for chunk in _file.chunks():
            data += chunk
        sqls = handle_dict(data)
        update_errors = update2db(sqls)
        if not update_errors:
            return render_to_response('save_db_success.html',context_instance=RequestContext(request))
        else:
            errors += update_errors
    elif request.method == 'POST':
        errors.append("you should choose a file as input")
    return render_to_response('save_db.html',{'errors':errors},context_instance=RequestContext(request))

folder = 'xml/'            
def update_from_report(request):
    errors = []
    data = request.body

    # write to file
    time_format = '%Y%m%d%H%M%S'
    file_name = folder + datetime.now().strftime(time_format) + '.xml'
    with open(file_name,'w') as f:
        f.write(data)

    sqls = handle_dict(data)
    update_errors = update2db(sqls)
    if not update_errors:
        return render_to_response('save_db_success.html',context_instance=RequestContext(request))
    
    return render_to_response('save_db.html',{'errors':errors},context_instance=RequestContext(request))


@login_required
def update(request):
    
    pass

def delete(request):
    
    pass

@login_required
def index(request):
    return render_to_response('index.html',context_instance=RequestContext(request))


@login_required
def add_probe(request):
    errors = []
    provinces = Province.objects.all()
    if 'prname' in request.POST and 'pr' in request.POST and 'gp' in request.POST:
        pn = request.POST['prname']
        p = request.POST['pr']
        g = request.POST['gp']
        if not pn:
            errors.append('Input a name')
        elif not p:
            errors.append('Choose a Province ')
        elif not g:
            errors.append('Input GPS')
        else:
            s = Probe.objects.filter(probe_name=pn)
            if not s:
                probes = Probe.objects.create(probe_name=pn,province=p,gps=g)
                probes.save()
                return render_to_response('add_probe_success.html',context_instance=RequestContext(request))
            else:
                errors.append('The probe has been exist!')
    return render_to_response('add_probe.html',{'errors':errors,'provinces':provinces},context_instance=RequestContext(request))

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
def show_probe(request):
    errors = []
    probe = Probe.objects.all()
    probe = probe.order_by('province')
    page = request.GET['page']
    contacts = sep_page(probe,page)
    return render_to_response('search_probe_result.html',{'errors':errors,'pro':contacts},context_instance=RequestContext(request))


@login_required
def show_ident(request):
    errors = []
    ident = Ident.objects.all()
    ident = ident.order_by('icao')
    page = request.GET['page']
    contacts = sep_page(ident,page)
    return render_to_response('search_ident_result.html',{'errors':errors,'idt':contacts},context_instance=RequestContext(request))

@login_required
def show_position(request):
    errors = []
    position = Position.objects.all()
    position = position.order_by('seen')
    page = request.GET['page']
    contacts = sep_page(position,page)
    return render_to_response('search_position_result.html',{'errors':errors,'po':contacts},context_instance=RequestContext(request))

@login_required
def show_vector(request):
    errors=[]
    vector = Vector.objects.all()
    vector = vector.order_by('seen')
    page = request.GET['page']
    contacts = sep_page(vector,page)
    return render_to_response('search_vector_result.html',{'ve':contacts},context_instance=RequestContext(request))



