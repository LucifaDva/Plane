#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse

from util import _validate, _parse, kml_link, output_dir
from tasks import output, wait_time, genkml, terminate_task
from datetime import datetime
from django.core.servers.basehttp import FileWrapper




def read_img(request):
    img = output_dir + '/' + 'airports.png'
    with open(img, 'r') as f:
        img_data = f.read()
    
    return HttpResponse(img_data, mimetype="image/png")

def read_from_url(request):
    if request.method == "GET":
        filename = request.GET['filename']
    else:
        return HttpResponse('empty', content_type='text/plain')
    path = output_dir + '/' + filename
    
    try:
        f = open(path)
        data = f.read()
    except:
        data = ''
        
    return HttpResponse(data, content_type='text/plain')

def output_kml(request):
    errors = []

    if request.method == "POST":
        filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.kml'
        path = output_dir + '/' + filename
        check_url = kml_link + filename
        
        sdate = request.POST.get('startdate')
        stime = request.POST.get('starttime')
        edate = request.POST.get('enddate')
        etime = request.POST.get('endtime')
        period_s = request.POST.get('period')
        starttime = sdate + ' ' + stime
        endtime = edate + ' ' + etime
        
        if not _validate(starttime) or not _validate(endtime):
            errors.append("input is EMPTY or FORMAT is not CORRECT.")
            return render(request, 'output_kml.html', {'errors':errors})

        """        
        if mode == 'static':
            genkml(starttime, endtime, path)
            try:
                f = open(path)
                response = HttpResponse(FileWrapper(f), content_type='application/force-download')
                response['content-disposition'] = 'attachment; filename=%s' % filename
                return response
            except:
                errors.append("error in download xml file")
                return render(request, 'output_kml.html', {'errors':errors})
        """
        
        # dynamic
        try:
            period_s = int(period_s)  #period_s is none
        except SyntaxError:
            errors.append("period syntax error")
            return render(request, 'output_kml.html', {'errors':errors})

        print "%s - %s" % (starttime, endtime)

        task = output.delay(starttime, endtime, period_s, path)
        return render(request, 'export_kml_success.html', {'check_url':check_url, 'wait_time':wait_time, 'taskid':task.id})
    
    return render(request, 'output_kml.html', {'errors':errors})

def cancel_task(request):
    if request.method == 'GET':
        taskid = request.GET['taskid']
        terminate_task(taskid)
        return render(request, 'cancel_success.html', {'taskid':taskid})
    else:
        errors.append("this method only be used by get.")
    return render(request, 'cancel_error.html', {'taskid':taskid, 'errors':errors})
        
        