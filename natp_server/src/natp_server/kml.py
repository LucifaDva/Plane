from django.shortcuts import render
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.db.models import Count

from datetime import datetime, timedelta
from models import Position, Ident, Vector, Probe

from util import _format



def output_kml(request):
    errors = []
    retstr = genkml(0, 0, 0)
    filename = write_to_xml(retstr)
    try:
        f = open(filename)
        response = HttpResponse(FileWrapper(f), content_type='application/force-download')
        response['content-disposition'] = 'attachment; filename=%s' % f.name
        return response
    except:
        errors.append("error in download xml file")
    return render(request, 'errors.html', {'errors':errors})



DEFAULT_FRESH_TIME = 180   # 30s

# FORMART: DDDDs / DDDDm / DDDDh
def parse_period(period):
    ret = DEFAULT_FRESH_TIME
    try:
        if period.endswith('s'):
            ret = int(period[:len(period)-1])
        elif period.endswith('m'):
            ret = 60 * int(period[:len(period)-1])
        elif period.endswith('h'):
            ret = 3600 * int(period[:len(period)-1])
    except Exception, err:
        print 'Parse configured period failed: %s' % period
        ret = DEFAULT_FRESH_TIME
        
    return ret

def write_to_xml(_retstr):
    file_name = 'output/trace_out.kml'
    with open(file_name, 'w') as f:
        f.write(_retstr)      # overwrite
    return file_name

def output(start, end, period):
    """
    time format:
        datetime
    period: 
        every period time to refresh the kml file
        format: xh / xm / xs
    """
    all = end - start
    _period = period
    _all = end-start
    
    back = front = start
    _seconds = 0
    while True:
        back = front
        front += timedelta(seconds=_period)
        if front < end:
            genkml(_format(back), _format(front))
        elif front > end:
            front = end
            genkml(_format(back), _format(front))
            break
        else:
            break

# time format (2013, 11, 27, 15, 3, 16, 772617)
def genkml(start, end):
    """
    time format:
        datetime    
    period: 
        every period time to refresh the kml file
        format: xh / xm / xs
    """
    retstr="""<?xml version="1.0" encoding="UTF-8"?>\n\
    <kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n\t<Style id="airplane">\n\t\t<IconStyle>\n\t\t\t<Icon><href>airports.png</href></Icon>\n\t\t</IconStyle>\n\t\
    </Style>\n\t<Style id="rangering">\n\t<LineStyle>\n\t\t<color>9f4f4faf</color>\n\t\t<width>2</width>\n\t</LineStyle>\n\t</Style>\n\t\
    <Style id="track">\n\t<LineStyle>\n\t\t<color>501400ff</color>\n\t\t<width>4</width>\n\t</LineStyle>\n\t</Style>"""

  
    #==========test=========
    _start = start
    _end = end
    _start = '2013-11-28 14:00:00'
    _end = '2013-11-28 15:00:00'

    retstr +=  """\t<Folder>\n\t\t<name>Aircraft locations</name>\n\t\t<open>0</open>"""
    
    temp = Position.objects.filter(seen__gt=_start).filter(seen__lt=_end)
    # get top 5 planes
    icaos_sort_by_count = temp.values('icao').annotate(icao_count=Count('icao')).order_by('icao_count')[:5]
    
    for ks in icaos_sort_by_count:
        _icao = ks['icao']
        positions = Position.objects.filter(icao__exact=_icao).order_by('-seen')
        if not positions:
            pass
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
        _ident = Ident.objects.filter(icao__exact=_icao)
        ident = ""
        if _ident:
            ident = _ident[0].ident
        
        _vector = Vector.objects.filter(icao__exact=_icao).order_by('seen')[:1]
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
#    write_to_xml(retstr)
    return retstr

if __name__ == "__main__":
    start = ""
    end = ""
    period = ""
    genkml(start, end, period)