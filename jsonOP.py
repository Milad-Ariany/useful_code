# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 16:17:45 2017

@author: Milad
"""

class JsonOP(object):
    def __init__(self, filePath):
        self.jsonFile = filePath
        
    def read(self):
        json = __import__('json')
        with open(self.jsonFile) as json_data:
            return json.load(json_data)
        return
        
    def write(self, data):
        json = __import__('json')
        try:
            with open(self.jsonFile, 'w') as f:
                f.write(json.dumps(data, default=lambda o: o.__dict__, indent=4))
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            print 'error in writing json'
        return