#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.db.models import Count
from natp_server.models import Position, Ident, Vector, Probe, Report
from datetime import datetime, timedelta
from natp_server.util import _format, _parse, _validate, write_to_xml
import time
from celery import current_app,task
import xml.etree.ElementTree as ET
from natp_server.util import img_link


wait_time = 5     # 5s
refresh_time = 2   # 1s
window_size = timedelta(minutes=-30)

@task
def handle_xml(data,ip):
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return {}

    sqls_dict = {}
    sqls = []
    for child in root:
        if child.tag == 'probe':
            sqls_dict.setdefault('probe', child.text)
        elif child.tag == 'content':
            try:
                v = eval(child.text)
            except:
                pass
            sqls.append(v)
    sqls_dict['sqls'] = sqls
    update2db(sqls_dict,ip)


def update2db(sqls,ip):
    """
    input
        sqls: {'probe':'XXX', 'sqls': [{ 'table_name':'XXX','values':{} },...]}
    return
        success: None
        error: errors
    """
    errors = []
    
    "对于没有对应probe的数据不接受"
    try:
        pr_name = sqls['probe']
    except KeyError:
        print 'Do not have probe key!'
        return errors
    
    try:
        pr = Probe.objects.get(probe_name=pr_name)
    except Probe.DoesNotExist:
        print 'DB does not have a probe_name with %s' % (pr_name)
        errors.append('DB does not have a probe_name with %s' % (pr_name))
        return errors
    except Probe.MultipleObjectsReturned:
        print 'DB has multi probe named %s.' % (pr_name)
        errors.append('DB has multi probe named %s.' % (pr_name))
        return errors
    
    print "=====>>>>> total sqls %s" % str(len(sqls['sqls']))
    index = 0
    
    # report record
    _report = Report.objects.create(ip=ip,count=len(sqls['sqls']),probe=pr)
    
    for sql in sqls['sqls']:
        index += 1
        print "hand sql[%s]: %s" % (index, sql)
        table_name = sql.get('table_name')
        values = sql.get('values')
        
        if values is None:
            print "%s :The value of the key 'values' is none" % sql
            errors.append("%s :The value of the key 'values' is none" % sql)
            return errors
        
        # vector
        if table_name == "vectors":
            _seen = _parse(values['seen'])
            _vector = Vector.objects.filter(icao__exact=values['icao'], seen__exact=_seen, \
                                            speed__exact=values['speed'], heading__exact=values['heading'], \
                                            vertical__exact=values['vertical'], probe__exact=pr)
            if not _vector:
                Vector.objects.create(icao=values['icao'],seen=_seen,speed=values['speed'],\
                                  heading=values['heading'],vertical=values['vertical'],probe=pr)
            else:
                for v in _vector:
                    v.updated = datetime.now()
                    v.save()

        # ident
        elif table_name=="ident":
            """
            handle encode error, just pass
            if ident is not starts_with 'ICAO'
            """
            try:
                ident_tag = int(values['ident'])
                continue
            except ValueError:
                pass
                
            try:
                _ident = Ident.objects.filter(icao__exact=values['icao'], probe__exact=pr).get(valid=True)
                ident_tag = values['ident']
                if _ident.ident == ident_tag:
                    _ident.updated = datetime.now()
                    _ident.save()
                else:
                    _ident.valid = False
                    _ident.updated = datetime.now()
                    _ident.save()
                    
                    _order = _ident.order
                    _order += 1
                    Ident.objects.create(icao=values['icao'], ident=values['ident'], probe=pr, order=_order, valid=True)
            except Ident.DoesNotExist:
                Ident.objects.create(icao=values['icao'], ident=values['ident'], probe=pr, order=1, valid=True)
            
            except Ident.MultipleObjectsReturned:
                pass
            
        # position
        elif table_name == "positions":
            _seen = _parse(values['seen'])
            _position = Position.objects.filter(icao__exact=values['icao'], seen__exact=_seen, \
                                                lat__exact=values['lat'], alt__exact=values['alt'], lon__exact=values['lon'], \
                                                probe__exact=pr)
            if not _position:
                Position.objects.create(icao=values['icao'], seen=_seen, lat=values['lat'],\
                                    alt=values['alt'], lon=values['lon'], probe=pr)
            else:
                for p in _position:
                    p.updated = datetime.now()
                    p.save()
        else:
            errors.append('%s :DB does not have a table_name with %s' % (sqls, table_name))
            pass
    return None


@task
def output(start, end, period, filename):
    """
    start, end:
        string like '2013-11-15 11:03:11'
    period:
        
    """
    _start = _parse(start)
    _end = _parse(end)
    _period = period

    
    back = front = _start
    time.sleep(wait_time)  # wait user to open googleearth
    while True:
        back = front
        front += timedelta(seconds=_period)
        if front < _end:
            genkml(back, front, filename)
            time.sleep(refresh_time)        # wait
        elif front > _end:
            front = _end
            genkml(back, front, filename)
            break
        else:
            break
        
    return 'Done'


def genkml(start, end, filename):
    """
    time format:
        datetime object
    """
    print "generate info between time %s - %s" % (start, end)

    retstr="""<?xml version="1.0" encoding="UTF-8"?>\n\
    <kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n\t<Style id="airplane">\n\t\t<IconStyle>\n\t\t\t<Icon><href>%s</href></Icon>\n\t\t</IconStyle>\n\t\
    </Style>\n\t<Style id="rangering">\n\t<LineStyle>\n\t\t<color>9f4f4faf</color>\n\t\t<width>2</width>\n\t</LineStyle>\n\t</Style>\n\t\
    <Style id="track">\n\t<LineStyle>\n\t\t<color>501400ff</color>\n\t\t<width>4</width>\n\t</LineStyle>\n\t</Style>""" % img_link

    _start = start
    _end = end
    if isinstance(start, basestring) or isinstance(start, unicode):
        _start = _parse(start) 
        _end = _parse(end)
    
    w_start = _start + window_size
    
    
    retstr +=  """\t<Folder>\n\t\t<name>Aircraft locations</name>\n\t\t<open>0</open>"""
    
    idents = Ident.objects.filter()
    
    temp = Position.objects.filter(seen__gt=_start).filter(seen__lt=_end)
    icaos_sort_by_count = temp.values('icao').annotate(icao_count=Count('icao')).order_by('icao_count')

    for ks in icaos_sort_by_count:
        _icao = ks['icao']
        idents = Ident.objects.filter(icao=_icao).filter(created__lte=_start).filter(updated__gte=_end)
        if not idents:
            idents = Ident.objects.filter(icao=_icao).filter(created__lte=_start)
        
        if not idents:
            continue
                
        positions = Position.objects.filter(seen__gt=w_start).filter(seen__lt=_end).filter(icao__exact=_icao).order_by('-seen')
        
        if not positions:
            continue
        else:
            i=0
            trackstr = ""
            for p in positions:
                if i==0:
                    lat = p.lat if p.lat is not None else 0
                    lon = p.lon if p.lon is not None else 0
                    alt = float(p.alt) if p.alt is not None else 0
                trackstr += " %s,%s,%f" % (p.lon, p.lat, float(p.alt)*0.3048)
                i += 1
        metric_alt = 0.3048*alt
        
        # get metadata
        ident = idents[0].ident
        print '%s - %s' % (_icao, ident)
        _vector = Vector.objects.filter(icao__exact=_icao).filter(seen__lte=_end).filter(seen__gte=_start).order_by('-seen')[:1]
        seen = 0
        speed = 0
        heading = 0
        vertical = 0
        if  _vector:
            seen = _vector[0].seen
            speed = _vector[0].speed
            heading = _vector[0].heading
            vertical = _vector[0].vertical

            
        retstr += "\n\t\t<Placemark>\n\t\t\t<name>%s</name>\n\t\t\t<Style><IconStyle>\
        <heading>%i</heading></IconStyle></Style>\n\t\t\t<styleUrl>#airplane</styleUrl>\n\t\t\t\
        <description>\n\t\t\t\t<![CDATA[Altitude: %s<br/>Heading: %i<br/>Speed: %i<br/>Vertical speed: %i<br/>\
        ICAO: %x<br/>Last seen: %s]]>\n\t\t\t</description>\n\t\t\t<Point>\n\t\t\t\t\
        <altitudeMode>absolute</altitudeMode>\n\t\t\t\t<extrude>1</extrude>\n\t\t\t\t\
        <coordinates>%s,%s,%i</coordinates>\n\t\t\t</Point>\n\t\t</Placemark>" \
        % (ident, heading, alt, heading, speed, vertical, _icao, seen, lon, lat, metric_alt, )
    
        retstr += "\n\t\t<Placemark>\n\t\t\t<styleUrl>#track</styleUrl>\n\t\t\t<LineString>\n\t\t\t\t\
        <extrude>0</extrude>\n\t\t\t\t<altitudeMode>absolute</altitudeMode>\n\t\t\t\t\
        <coordinates>%s</coordinates>\n\t\t\t</LineString>\n\t\t</Placemark>" % (trackstr,)
        
    retstr += '\n\t</Folder>\n</Document>\n</kml>'
    write_to_xml(_retstr=retstr, filepath=filename)

def terminate_task(taskid):
    current_app.control.revoke(taskid, terminate=True)