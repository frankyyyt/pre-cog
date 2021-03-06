#
# Copyright 1980-2012 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from math import pi
from gnuradio import gr
from gruel import pmt
from gnuradio.digital import packet_utils
import gnuradio.digital as gr_digital
import gnuradio.extras #brings in gr.block
import Queue
import time
import math



# /////////////////////////////////////////////////////////////////////////////
#                   Virtual Channel Mux
# /////////////////////////////////////////////////////////////////////////////

class virtual_channel_mux(gr.block):
    """
    Mux data from multiple sources and add header for routing
    """
    def __init__(
        self,port_count
    ):
        """
        The inputs are a pmt message blob.
        Non-blob messages will be ignored.
        """

        gr.block.__init__(
            self,
            name = "virtual_channel_mux",
            in_sig = None,
            out_sig = None,
            num_msg_inputs = port_count,
            num_msg_outputs = 1,
        )
    
        self.mgr = pmt.pmt_mgr()
        for i in range(64):
            self.mgr.set(pmt.pmt_make_blob(10000))
        
    def work(self, input_items, output_items):
        
        while(1):
            try: msg = self.pop_msg_queue()
            except: return -1

            if not pmt.pmt_is_blob(msg.value): 
                print "not a blob - virtual mux"
                continue

            #insert header byte so demux can route to appropriate output
            data = numpy.concatenate([numpy.array([msg.offset]),pmt.pmt_blob_data(msg.value)])
            
            blob = self.mgr.acquire(True) #block
            pmt.pmt_blob_resize(blob, len(data))
            pmt.pmt_blob_rw_data(blob)[:] = data
            self.post_msg(0,msg.key,blob,pmt.pmt_string_to_symbol('mux')) #pass incoming key for transparency
            
