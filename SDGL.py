# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 16:13:36 2017

@author: Milad
"""

import operations

globalRawSDGLs = r"C:\Users\Milad\Desktop\My Project\Data\Fetched\csv\StationDeviceGroup.csv"
oufOfLineStationDeviceGroupID = "outofline"

class StationDeviceGroupLocation(object): 
    def __init__(self, rawData = None):
        self.ID = None
        #self.groupID = None
        self.groupName = None
        #self.deviceID = None
        self.deviceName = None
        #self.stationID = None
        self.stationName = None
        self.firstTakt = None
        self.lastTakt = None
        self.locationOrder = None
        self.length = None
        self.line = None
        self.name = None
        self.rawSource = rawData
              
    def populate(self, key):
        op = operations.Operate()
        self.firstTakt = op.Cast(self.rawSource['FirstTakt'], str)
        self.lastTakt = op.Cast(self.rawSource['LastTakt'], str)
        self.locationOrder = op.Cast(self.rawSource['LocationOrder'], str)
        self.length = op.Cast(self.rawSource['Length'], str)
        self.line = op.Cast(self.rawSource['Line'], str)
        #self.stationID = op.Cast(self.rawSource['StationID'], str)
        self.stationName = op.Cast(self.rawSource['StationName'], str)
        #self.groupID = op.Cast(self.rawSource['GroupID'], str)
        self.groupName = op.Cast(self.rawSource['GroupName'], str)
        #self.deviceID = op.Cast(self.rawSource['DeviceID'], str)
        self.deviceName = op.Cast(self.rawSource['DeviceName'], str)
        if key == "device":
            self.ID = op.Cast(self.rawSource['DeviceName'], str)
        elif key == "group":
            self.ID = op.Cast(self.rawSource['GroupName'], str)
        elif key == "station":
            self.ID = op.Cast(self.rawSource['StationName'], str)                 
        elif key == "location":
            self.ID = op.Cast(self.rawSource['LocationOrder'], str)
        return
        
    def getDevice(self):
        return self.populate("device")
    
    def getGroup(self):
        return self.populate("group")
        
    def getStation(self):
        return self.populate("station")
        
    def getLocation(self):
        return self.populate("location")