#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import resource

def close_all():
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = 1024
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:
            pass

def get_devnull():
    if (hasattr(os, "devnull")):
        return os.devnull
    else:
        return "/dev/null"



def daemonize():
    pid = os.fork()
    if pid != 0:
        return pid
  
    os.setsid()
    # signal.signal(signal.SIGHUP, signal.SIG_IGN)
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    close_all()
    os.open(get_devnull(), os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)
    return 0