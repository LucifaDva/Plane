#!/usr/bin/env python
# -*- coding: utf-8 -*-

import memcache
mc = memcache.Client(['127.0.0.1:11111'],debug=1)
idents = Ident.objects.all()
idents = idents.order_by('ident')
for x in idents:
    icao =  x.icao
    key_name = 'memvector_'+str(icao)
    mc_data = mc.get(key_name)
    if mc_data:
        print "%s hs benn in cache!!"%str(icao)
    else:
        print "Try to input %s in memcache"%str(icao)
        ident = x.ident
        v = Vector.objects.filter(icao=icao)
        v= v.order_by('-seen')
        lst = []
        date = []
        for d in v:
            da = d.seen[:10]
            s = d.seen[:14]+str(int(d.seen[14])*10+int(d.seen[15])+1)+d.seen[16:]
            b = d.seen[:14]+str(int(d.seen[14])*10+int(d.seen[15])-1)+d.seen[16:]
            d.position = Position.objects.filter(icao=icao,probe=d.probe,seen__range=(b,s))
            if d.position:
                d.position = d.position[0]
            if da not in date:
                date.append(da)
                lst.append(d)
                d.flag = 1
                d.date = da
        data_lst = []
        data_lst.append(ident)
        data_lst.append(lst)
        data_lst.append(v)
        mc.set(key_name,data_lst)

