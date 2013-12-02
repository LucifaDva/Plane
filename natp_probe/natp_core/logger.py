#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler

def get_logger(name, filename = '', \
               format = '[%(asctime)s] %(levelname)-7s %(name)s %(lineno)d %(threadName)s %(message)s', \
               level = logging.DEBUG, default = False):
    
    logger = logging.getLogger(name)
    if filename:
        handler = RotatingFileHandler(filename)
        handler.setFormatter(logging.Formatter(format))
        if default:
            logging.root.addHandler(handler)
        else:
            logger.addHandler(handler)
    if default:
        logging.root.setLevel(level)
    else:
        logger.setLevel(level)
    
    return logger