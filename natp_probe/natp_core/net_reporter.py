#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import time
from threading import Thread, Lock
from Queue import Queue

class net_reporter(Thread):

    XMLHEAD = """<?xml version='1.0' encoding='UTF-8'?>\n"""
    MAX_REP_NUM = 100  # can read from config file
    DEFAULT_TIMEOUT = 120
    
    def __init__(self, probe_name, timeout, max_rep_num, endpoint, queue, cert=None, cacert=None):
        # self._queue instance of gr.msg_queue
        super(net_reporter, self).__init__()
        self._probe_name = probe_name
        self._queue = queue
        self._timeout = self.__parse_timeout(timeout.lower())
        self._max_rep_num = max_rep_num
        self._endpoint = endpoint
        
        self._cert = cert
        self._cacert = cacert
        
        self.done = False
        self.setDaemon(1)
        self.start()
        
    def __del__(self):
        self._queue = None
    
    # timeout in config. file:
    # FORMART: DDDDs / DDDDm / DDDDh
    def __parse_timeout(self, timeout):
        ret = net_reporter.DEFAULT_TIMEOUT
        try:
            if timeout.endswith('s'):
                ret = int(timeout[:len(timeout)-1])
            elif timeout.endswith('m'):
                ret = 60 * int(timeout[:len(timeout)-1])
            elif timeout.endswith('h'):
                ret = 3600 * int(timeout[:len(timeout)-1])
        except Exception, err:
            print >> sys.stderr, 'Parse configured TIMEOUT failed: %s' % self._timeout
            ret = net_reporter.DEFAULT_TIMEOUT
            
        return ret
    #
    def run(self):
        while not self.done:
            # 1. generate XML
            # 2. exec. curl cmd
            xmlstr = self.__genXML()
            try:
                self.__sendReport(xmlstr)
            except Exception, e:
                print >> sys.stderr, 'Push tracing records failed: %s' %str(e)
            #
            time.sleep(self._timeout)
        #
        self.done = True
        self._queue = None
    #
    def __genXML(self):
        retstr = ''
        acc_num = 0
        if not self._queue.empty():
            while not self._queue.empty() and acc_num <= self._max_rep_num:
                sql = self._queue.get()

                retstr += "<content>%s</content>\n" % sql
                acc_num += 1
        else:
            print "=====>>>>> net_report queue empty."

        return net_reporter.XMLHEAD + "<sql>\n<probe>%s</probe>\n%s</sql>" % (self._probe_name, retstr)
    #
    
    def __sendReport(self, xmlstr):
        
        tempH = self.exec_cmd("mktemp")
        
        curl_args = '-X PUT -H "Content-Type: text/xml" -H "Accept: text/xml" --cert %s --cacert %s -d "%s" --dump-header %s %s' \
                    % (self._cert, self._cacert, xmlstr, tempH, self._endpoint)
        # use http temporarily
        curl_args = '-X PUT -H "Content-Type: text/xml" -H "Accept: text/xml" -d "%s" --dump-header %s %s' \
                    % (xmlstr, tempH, self._endpoint)

        curl_ret = os.system('curl %s 1>/dev/null 2>/dev/null' % curl_args)
        if curl_ret != 0:
            raise Exception, 'curl  error!'
        else:
            try:
                fd = open(tempH)
                ret = fd.readline()
            except:
                fd.close()
                raise Exception, 'curl error!'
            finally:
                fd.close()
            #
            ret = ret.strip()
            print >> sys.stderr, ret[ret.find(' ') + 1:]  #200 OK
    #
    def exec_cmd(self, cmd):
        pipe=os.popen(cmd,"r")
        ret= pipe.read()
        pipe.close()
        rett = ret.rstrip('\n')

        return rett

if __name__ == "__main__":
    
    pass