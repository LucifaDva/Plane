import xml.etree.ElementTree as ET
from models import Probe, Vector, Position, Ident

from datetime import datetime


FORMAT = "%Y-%m-%d %H:%M:%S"
def _format(_time):
    return _time.strftime(FORMAT)

def get_data(filename):
    data = ''
    with open(filename) as f:
        for line in f:
            data += line
    return data

def handle_dict(data):
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
    return sqls_dict

def update2db(sqls):
    """
    input
        sqls: {'probe':'XXX', 'sqls': [{ 'table_name':'XXX','values':{} },...]}
    return
        success: None
        error: errors
    """
    errors = []
    pr_name = sqls.get('probe')
    if pr_name is None:
        print 'Do not have probe key!'
        errors.append('Do not have probe key!')
        return errors
    try:
        pr = Probe.objects.get(probe_name=pr_name)
    except Probe.DoesNotExist:
        print 'DB does not have a probe_name with %s' % (pr_name)
        errors.append('DB does not have a probe_name with %s' % (pr_name))
        return errors
    for sql in sqls['sqls']:
        print "hand sql: %s" % sql
        table_name = sql.get('table_name')
        values = sql.get('values')
        if values is None:
            print "%s :The value of the key 'values' is none" % sql
            errors.append("%s :The value of the key 'values' is none" % sql)
            return errors
        
        if table_name == "vectors":
            _vector = Vector.objects.filter(icao__exact=values['icao'], seen__exact=values['seen'], \
                                            speed__exact=values['speed'], heading__exact=values['heading'], \
                                            vertical__exact=values['vertical'], probe__exact=pr)
            if not _vector:
                Vector.objects.create(icao=values['icao'],seen=values['seen'],speed=values['speed'],\
                                  heading=values['heading'],vertical=values['vertical'],probe=pr)
            else:
                for v in _vector:
                    v.updated = datetime.now()
                    v.save()

        elif table_name=="ident":
            _ident = Ident.objects.filter(icao__exact=values['icao'])
            if not _ident:
                Ident.objects.create(icao=values['icao'],ident=values['ident'],probe=pr)
            else:
                for i in _ident:
                    i.ident = values['ident']
                    i.probe = pr
                    i.updated = datetime.now()
                    i.save()

        elif table_name == "positions":
            _position = Position.objects.filter(icao__exact=values['icao'], seen__exact=values['seen'], \
                                                lat__exact=values['lat'], alt__exact=values['alt'], lon__exact=values['lon'], \
                                                probe__exact=pr)
            if not _position:
                Position.objects.create(icao=values['icao'],seen=values['seen'],lat=values['lat'],\
                                    alt=values['alt'],lon=values['lon'],probe=pr)
            else:
                for p in _position:
                    p.updated = datetime.now()
                    p.save()
        else:
            errors.append('%s :DB does not have a table_name with %s' % (sqls, table_name))
            pass
    return None

# datetime format (2013, 11, 27, 15, 3, 16, 772617)
def get_time():
    pass

def kml():
    pass