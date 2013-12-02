#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gnuradio import gr, gru, optfir, eng_notation, blks2
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import time, os, sys, threading
from string import split, join
import air_modes
import gnuradio.gr.gr_threading as _threading
import csv
from air_modes.exceptions import *

import config as Config
import logger as Logger
import utils as Utils 
import net_reporter as Net_reporter

import sql_queue as Queue

DEFAULT_CONFIG = ''

my_position = None

class top_block_runner(_threading.Thread):
    def __init__(self, tb):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.tb = tb
        self.done = False
        self.start()

    def run(self):
        self.tb.run()
        self.done = True

class adsb_rx_block (gr.top_block):
    def __init__(self, options, args, queue):
        gr.top_block.__init__(self)
    
        self.options = options
        self.args = args
        rate = int(options.rate)
        use_resampler = False

        if options.filename is None and options.udp is None and not options.rtlsdr:
            #UHD source by default
            from gnuradio import uhd
            self.u = uhd.single_usrp_source(options.args, uhd.io_type_t.COMPLEX_FLOAT32, 1)
            time_spec = uhd.time_spec(0.0)
            self.u.set_time_now(time_spec)
            
            #if(options.rx_subdev_spec is None):
            #  options.rx_subdev_spec = ""
            #self.u.set_subdev_spec(options.rx_subdev_spec)
            if not options.antenna is None:
                self.u.set_antenna(options.antenna)
                
            self.u.set_samp_rate(rate)
            rate = int(self.u.get_samp_rate()) #retrieve actual
    
            if options.gain is None: #set to halfway
                g = self.u.get_gain_range()
                options.gain = (g.start()+g.stop()) / 2.0
        
            if not(self.tune(options.freq)):
                print "Failed to set initial frequency"
        
            print "Setting gain to %i" % options.gain
            self.u.set_gain(options.gain)
            print "Gain is %i" % self.u.get_gain()
        
        elif options.rtlsdr: #RTLSDR dongle
            import osmosdr
            self.u = osmosdr.source_c(options.args)
            self.u.set_sample_rate(3.2e6) #fixed for RTL dongles
            if not self.u.set_center_freq(options.freq):
                print "Failed to set initial frequency"
    
            self.u.set_gain_mode(0) #manual gain mode
            if options.gain is None:
                options.gain = 34
                
            self.u.set_gain(options.gain)
            print "Gain is %i" % self.u.get_gain()

            use_resampler = True
        else:
            if options.filename is not None:
                self.u = gr.file_source(gr.sizeof_gr_complex, options.filename)
            elif options.udp is not None:
                self.u = gr.udp_source(gr.sizeof_gr_complex, "localhost", options.udp)
            else:
                raise Exception("No valid source selected")
        
        print "Rate is %i" % (rate,)
        pass_all = 0
        if options.output_all:
            pass_all = 1

        self.rx_path = air_modes.rx_path(rate, options.threshold, queue, options.pmf)
        
        if use_resampler:
            self.lpfiltcoeffs = gr.firdes.low_pass(1, 5*3.2e6, 1.6e6, 300e3)
            self.resample = blks2.rational_resampler_ccf(interpolation=5, decimation=4, taps=self.lpfiltcoeffs)
            self.connect(self.u, self.resample, self.rx_path)
        else:
            self.connect(self.u, self.rx_path)

    def tune(self, freq):
        result = self.u.set_center_freq(freq, 0)
        return result

def printraw(msg):
    print '[RAW] ' + msg

def do_main(options, args):
    
    config_file = options.config
    if not config_file:
        config_file = DEFAULT_CONFIG
    
    config = Config.load_config(config_file)
    
    logfile = os.path.expanduser(config.get_opt(Config.OPT_GEN_LOGFILE))
    if not os.path.exists(logfile):
        print >> sys.stderr, 'configured logfile: %s does not exist, exit.' % logfile
        exit(1)
    
    logger = Logger.get_logger('natp_probe.modes_probe', logfile, default=True)
    logger.info("=====>>>>> NAPT_probe initial config and logfile completed.")
    
    #
    net_reporter_q = Queue.sql_queue(0)
    msg_q = gr.msg_queue(0)
    
    outputs = [] #registry of plugin output functions
#    updates = [] #registry of plugin update functions

    if options.location is not None:
        global my_position
        reader = csv.reader([options.location], quoting=csv.QUOTE_NONNUMERIC)
        my_position = reader.next()

#    if options.raw is True:
#        rawport = air_modes.raw_server(9988) #port
#        outputs.append(rawport.output)
#        outputs.append(printraw)
#        updates.append(rawport.add_pending_conns)
#    if options.kml is not None:
#        #we spawn a thread to run every 30 seconds (or whatever) to generate KML
#        dbname = 'adsb.db'
#        lock = threading.Lock()
#        sqldb = air_modes.output_sql(my_position, dbname, lock) #input into the db
#        kmlgen = air_modes.output_kml(options.kml, dbname, my_position, lock) #create a KML generating thread to read from the db
#        outputs.append(sqldb.output)

    if options.net_reporter:
        global my_position
        # We spawn a thread to run every [config.timeout] seconds to send tracing records.
        dbname = 'adsb.db'
        lock = threading.Lock()
        # input the records into the local db file.
        sqldb = air_modes.output_sql(my_position, dbname, lock)
        # create a networked reporter thread to send sql records.
        net_reporter = Net_reporter.net_reporter( config.get_opt(Config.OPT_PROBE_NAME), config.get_opt(Config.OPT_NETR_TIMEOUT),\
                                                 config.get_opt(Config.OPT_NETR_MAX_REP_NUM), config.get_opt(Config.OPT_NETR_ENDPOINT), net_reporter_q)

        if options.kml:
            kmlgen = air_modes.output_kml(options.kml, dbname, my_position, lock)
        outputs.append(sqldb.output)
        logger.info("=====>>>>> NAPT_probe network_reporter initialization completed.")
        
    if options.no_print is not True:
        global my_position
        outputs.append(air_modes.output_print(my_position).output)
#    if options.sbs1 is True:
#        sbs1port = air_modes.output_sbs1(my_position, 30003)
#        outputs.append(sbs1port.output)
#        updates.append(sbs1port.add_pending_conns)
#    if options.multiplayer is not None:
#        [fghost, fgport] = options.multiplayer.split(':')
#        fgout = air_modes.output_flightgear(my_position, fghost, int(fgport))
#        outputs.append(fgout.output)
    
    fg = adsb_rx_block(options, args, msg_q)
    runner = top_block_runner(fg)
    
    while 1:
        try:
            # main message handler
            if not msg_q.empty_p() :
                while not msg_q.empty_p() :
                    msg = msg_q.delete_head() #blocking read
#                    for out in outputs:
#                        if isinstance(out, air_modes.output_sql):
#                            try:
#                                sql_cmd = out(msg.to_string())
#                            except air_modes.ADSBError:
#                                #@todo: print exception into log file.
#                                logger.error("=====>>>>> modes_probe except ADSBError.")
#                                pass
#                            if sql_cmd is not None:
#                                net_reporter_q.insert_tail(gr.message_from_string(sql_cmd))
#                                logger.debug("INSERT sql commands: %s", sql_cmd)
#                        else:
#                            try:
#                                out(msg.to_string())
#                            except air_modes.ADSBError:
#                                pass
                    for out in outputs:
                        try:
#                            if isinstance(out, air_modes.output_sql):
                            if getattr(sqldb, out.__name__, None):
                                if options.kml:
                                    # write sql to db
                                    out(msg.to_string())
                                # report to server
                                sql_dict = sqldb.get_sql_dict(msg.to_string())
                            
                                if sql_dict is not None:
                                    net_reporter_q.put(str(sql_dict))
                                    logger.debug("INSERT sql dict: %s", sql_dict)
                            else:
                                out(msg.to_string())
                        except air_modes.ADSBError:
                                logger.error("=====>>>>> modes_probe except ADSBError.")
            elif runner.done:
                raise KeyboardInterrupt
            else:
                time.sleep(0.1)
    
        except KeyboardInterrupt:
            fg.stop()
            runner = None
            if options.net_reporter:
                net_reporter.done = True
            if options.kml is not None:
                kmlgen.done = True
                
            logger.info("=====>>>>> NAPT_probe finished.")
            break
  

if __name__ == '__main__':
    from optparse import OptionParser
    
    usage = """ Start Air tracing based on Mode S. \n
    usage: %prog [options] output_filename    
    """

    parser = OptionParser(option_class=eng_option, usage=usage)
    
    parser.add_option("-C", "--config", type="string", default=None,
            help="filename for configure file", metavar="CONFIG")
    parser.add_option("-N", "--net_reporter", action="store_true", default=False,
            help="enable networked tracing reproting")
    
    parser.add_option("-R", "--rx-subdev-spec", type="string",
            help="select USRP Rx side A or B", metavar="SUBDEV")
    parser.add_option("-A", "--antenna", type="string",
            help="select which antenna to use on daughterboard")
    parser.add_option("-D", "--args", type="string",
            help="arguments to pass to UHD/RTL constructor", default="")
    parser.add_option("-T", "--threshold", type="eng_float", default=5.0,
            help="set pulse detection threshold above noise in dB [default=%default]")
    parser.add_option("-F","--filename", type="string", default=None,
            help="read data from file instead of USRP")
    parser.add_option("-K","--kml", type="string", default=None,
            help="filename for Google Earth KML output")
    
    parser.add_option("-f", "--freq", type="eng_float", default=1090e6,
            help="set receive frequency in Hz [default=%default]", metavar="FREQ")
    parser.add_option("-g", "--gain", type="int", default=None,
            help="set RF gain", metavar="dB")
    parser.add_option("-r", "--rate", type="eng_float", default=4000000,
            help="set ADC sample rate [default=%default]")
    parser.add_option("-a","--output-all", action="store_true", default=False,
            help="output all frames")
    
#    parser.add_option("-P","--sbs1", action="store_true", default=False,
#            help="open an SBS-1-compatible server on port 30003")
#    parser.add_option("-w","--raw", action="store_true", default=False,
#            help="open a server outputting raw timestamped data on port 9988")
    parser.add_option("-n","--no-print", action="store_true", default=False,
            help="disable printing decoded packets to stdout")
    parser.add_option("-l","--location", type="string", default=None,
            help="GPS coordinates of receiving station in format xx.xxxxx,xx.xxxxx")
    parser.add_option("-u","--udp", type="int", default=None,
            help="Use UDP source on specified port")
#    parser.add_option("-m","--multiplayer", type="string", default=None,
#            help="FlightGear server to send aircraft data, in format host:port")
    parser.add_option("-d","--rtlsdr", action="store_true", default=False,
            help="Use RTLSDR dongle instead of UHD source")
    parser.add_option("-p","--pmf", action="store_true", default=False,
            help="Use pulse matched filtering")
                      
    (options, args) = parser.parse_args()
    
    do_main(options, args)