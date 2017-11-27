# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 16:11:18 2017

@author: Milad
"""

import datetime as dt
class Operate(object):
#    def funcFormatValue(val):
#        val = str(val)
#        if "null" in val:
#            return None
##        if "-1" in val and len(val) == 2:
##            return None
##        if val == -1:
##            return None
#        return val
#    
    def Cast(self, val, to_type, default = None):
        if val is None or val == "":
            return default
        if to_type == str:
            if "null" in str(val):
                return None
        try:
            return to_type(val)
        except (ValueError, TypeError):
            return default
            
    def dataFrame(self, rawSource):
        pd = __import__('pandas')
        out = pd.read_csv(rawSource, ';')
        return out
        
    def stringToDatetime(self, inp):      
        #import re
        #match=re.search(r'(\d-\d+-\d+-\d+.\d+.\d+.\d+)','The date is 20987617-01-09-06.04.38.100131.l')
        #match.group(1)
        return dt.datetime.strptime(inp, "%Y-%m-%d-%H.%M.%S.%f")

    def datetimeDiffinSec(self, dt1, dt2):
        if type(dt1) == dt.datetime and type(dt2) == dt.datetime:
            return long((dt1 - dt2).total_seconds()*1000)
        dt1 = self.stringToDatetime(dt1)
        dt2 = self.stringToDatetime(dt2)
        return long((dt1 - dt2).total_seconds()*1000)