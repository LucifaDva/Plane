#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import Probe, Vector, Position, Ident
from datetime import datetime
import os

kml_link = "http://www.natp.com/kml/readkml?filename="

img_link = "http://www.natp.com/kml/readimg"

output_dir = os.path.abspath(os.path.dirname(__file__)) + '/output'
default_kml_path = output_dir + '/' + 'output.kml'

FORMAT = "%Y-%m-%d %H:%M:%S"

def write_to_xml(_retstr='', filepath=default_kml_path):
    file_name = filepath
    with open(file_name, 'w') as f:
        f.write(_retstr)      # overwrite

def check_timestamp():
    """
    return (max, min) seen time in position
    """
    max_timestamp = Position.objects.all().order_by('-seen')[:1]
    min_timestamp = Position.objects.all().order_by('seen')[:1]

    return max_timestamp, min_timestamp

def _validate(_time):
    """
     to validate the _time is in format 'FORMAT'
    """
    if _parse(_time):
        return _time
    else:
        return None

# return time in string format    
def _format(_time, _format=FORMAT):
    return _time.strftime(_format)

# return time in datetime object format
def _parse(_time, _format=FORMAT):
    try:
        _datetime = datetime.strptime(_time, _format)
    except ValueError:
        _datetime = None
    return _datetime


def get_data(filename):
    data = ''
    with open(filename) as f:
        for line in f:
            data += line
    return data