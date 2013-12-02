#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import os

class ConfigException(Exception):
    """A simple exception class used for configuration exceptions"""
    pass

CONFIG_SEC = ('general', 'net_reporter')

OPT_GEN_LOGFILE = 'log_file'
OPT_PROBE_NAME ='probe_name'
#
OPT_NETR_ENDPOINT = 'endpoint'
OPT_NETR_TIMEOUT = 'timeout'
OPT_NETR_MAX_REP_NUM = 'max_rep_num'
OPT_NETR_CERT = 'client_cert'
OPT_NETR_CACERT = 'ca_cert'

CONFIG_OPTIONS = (OPT_GEN_LOGFILE, OPT_PROBE_NAME, OPT_NETR_ENDPOINT, OPT_NETR_MAX_REP_NUM, \
                  OPT_NETR_TIMEOUT, OPT_NETR_CERT, OPT_NETR_CACERT)
#
class Config:
    
    def __init__(self, cfg, exec_base):       
        self._options = {}
        self.__load_all_opt(cfg)
        self._exec_base = exec_base
        
    def __load_all_opt(self, cfg):
        
        for sec in CONFIG_SEC:
            ll = cfg.items(sec)
            for (opt, val) in ll:
                self._options[opt] = val
    #
    def get_opt(self, opt):
        try:
            val = self._options[opt]
        except KeyError, e:
            val = None
        return val
    
    def get_execbase(self):
        return self._exec_base

def load_config(config, exec_base = None):
    fd = open (config, "r")
    c = ConfigParser.ConfigParser()
    c.readfp(fd)
    
    cfg = Config(c, exec_base)
    return cfg


if __name__ == '__main__':
    cofig_file = './pwd_cert.conf'
    cfg = load_config(cofig_file)
        
    for opt in CONFIG_OPTIONS:
        val = cfg.get_opt(opt)
        print type(val)
        print 'Option: %s; Value: %s' %(opt, val)        
