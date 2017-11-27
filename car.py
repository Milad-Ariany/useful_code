# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 16:35:19 2017

@author: Milad
"""

import parenthood as ph
import operations
import defectProfile as dfct
import SDGL as sdgl

class Car(object): 
    def __init__(self, rawData = None):
        self.ID = None
        self.UOrder = None
        self.model = None
        self.motorType = None
        self.gearType = None
        self.FGSTTM = None
        self.FGSTPZ = None
        self.FGSTMJ = None
        self.FGSTWK = None
        self.FGSTLFD = None
        self.F500_TS = None
        self.F510_TS = None
        self.F590_TS = None
        self.F600_TS = None
        self.G200_TS = False
        self.G300_TS = False
        self.ELFIS = False
        self.rework = False
        self.defects = []
        self.defectsParenthood = None
        self.rawSource = rawData
        
    def populate(self):
        op = operations.Operate()
        self.ID = op.Cast(self.rawSource['KANR'], str)
        self.model = self.rawSource['MODELL']
        self.motorType = self.rawSource['MOTORKB']
        self.gearType = self.rawSource['GETRIEBEKB']          
        self.FGSTTM = self.rawSource['FGSTTM']
        self.FGSTPZ = self.rawSource['FGSTPZ']
        self.FGSTMJ = self.rawSource['FGSTMJ']  
        self.FGSTWK = self.rawSource['FGSTWK'] 
        self.FGSTLFD = self.rawSource['FGSTLFD'] 
        self.F500_TS = self.rawSource['F500'] 
        self.F510_TS = self.rawSource['F510'] 
        self.F590_TS = self.rawSource['F590'] 
        self.F600_TS = self.rawSource['F600'] 
        self.G200_TS = self.rawSource['G200'] 
        self.G300_TS = self.rawSource['G300'] 
        self.ELFIS = self.rawSource['ELFIS']  
        return
        
    def setDefectsParenthood(self):
        parenthoodObj = ph.Matrix()
        parenthoodObj.generate(self.defects)
        # it should be placed in a list to follow json format
        self.defectsParenthood = [parenthoodObj]       

    def defectsTaktResolution(self):
        op = operations.Operate()
        processedLoc = []
        stat = dfct.defectStatus
        for d in self.defects:
            if op.Cast(d.status, int) == stat.multiLine.value:
                continue
            dList = []
            loc = d.detectionLocationOrder
            dList = self.getDefectsInaLocation(loc, processedLoc)
            self.mapTimeToTakt(loc, dList);
    
            loc = d.resolutionLocationOrder
            dList = self.getDefectsInaLocation(loc, processedLoc)
            self.mapTimeToTakt(loc, dList);
        return

    def getDefectsInaLocation(self, loc, processedLoc):
        if loc is None or loc in processedLoc:
            return []
        stat = dfct.defectStatus
        op = operations.Operate()
        dList = []
        processedLoc.append(loc)
            # Find all defects detected or resolved in this position and store them
        for d in self.defects: # Read all errors detected or resolved in this position and store them
            if op.Cast(d.status, int) == stat.multiLine.value:
                continue
            if (d.detectionLocationOrder == loc) or (d.resolutionLocationOrder == loc):
                dList.append(d);
        return dList
    
    def dataFrame(self, filePath):
        pd = __import__('pandas')
        out = pd.read_csv(filePath, ',')
        return out
        
    def fetchSDGL(self, key):
        out = dict()
        op = operations.Operate()
        rawData = op.dataFrame(sdgl.globalRawSDGLs)
        for inx in range(len(rawData)):
            rawSDGL = rawData.iloc[inx, ]
            Obj = sdgl.StationDeviceGroupLocation(rawSDGL)
            if key.lower() == "g":
                Obj.getGroup()
            elif key.lower() == "l":
                Obj.getLocation()
            elif key.lower() == "s":
                Obj.getStation()
            elif key.lower() == "d":
                Obj.getDevice()
            if Obj.ID not in out:
                out[Obj.ID] = Obj
        return out
        
    def mapTimeToTakt(self, loc, defectsList):
        locationDict = self.fetchSDGL("l")
        if loc not in locationDict or defectsList == None or len(defectsList) == 0:
            return
        
        locObj = locationDict.get(loc)
    #    print "-------------------------------------------------------"
        if len(defectsList) == 1: # if only 1 event happened in this position, this defect does not affect any other defect
            d = defectsList[0];
            if d.detectionLocationOrder == loc:
                d.detectionTakt = locObj.firstTakt
            if d.resolutionLocationOrder == loc:
                d.resolutionTakt = locObj.lastTakt
    #        print "Loc: %s" % (loc)
    #        print "Det_ID: %s, Det_T: %s, Det_Loc: %s, Det_Takt:%s, Res_T: %s, Res_Loc: %s, Res_Takt:%s" % (d["relationalDefectID"], d["detectionTime"], d["detectionLocationOrder"], d["detectionTakt"], d["resolutionTime"], d["resolutionLocationOrder"], d["resolutionTakt"])
            return;
            
        else:       
            maxMinDict = self.getMaxMinTimeinLocation(loc, defectsList)
            maxTimeVal = maxMinDict.get("max", None)
            minTimeVal = maxMinDict.get("min", None)
    #        print "Loc: %s, Max:%s, Min:%s, First_Takt: %s, Last_Takt:%s, ds:%s" % (loc, maxTimeVal, minTimeVal, locObj.firstTakt, locObj.lastTakt, len(defectsList))
            for d in defectsList: # By normalizing times based on number of takts in a position, the TAKT number where the event happens will be generated
                if d.detectionLocationOrder == loc: # If the DetPos of the event was located in this position, then it should be normalized
                    d.detectionTakt = self.normalize (minTimeVal, maxTimeVal, locObj.firstTakt, locObj.lastTakt, d.detectionTime)
                if d.resolutionLocationOrder == loc: # If the ResPos of the event was located in this position, then it should be normalized
                    d.resolutionTakt = self.normalize (minTimeVal, maxTimeVal, locObj.firstTakt, locObj.lastTakt, d.resolutionTime)
                #print "Det_ID: %s, Det_T: %s, Det_Loc: %s, Det_Takt:%s, Res_T: %s, Res_Loc: %s, Res_Takt:%s" % (d["relationalDefectID"], d["detectionTime"], d["detectionLocationOrder"], d["detectionTakt"], d["resolutionTime"], d["resolutionLocationOrder"], d["resolutionTakt"])
        return;

    def getMaxMinTimeinLocation(self, loc, defectsList):
        op = operations.Operate()
        if len(defectsList) == 0:
            return dict()
        op = operations.Operate()    
        minTimeVal = op.stringToDatetime(defectsList[0].detectionTime) 
        maxTimeVal = op.stringToDatetime(defectsList[0].resolutionTime)
        # it is possible that an error happens in one position and has been resolved in another
        # so we should only consider that event of the error [Res, Det] which happened in the
        # current position. that is why we use d[detectionTime, resolutionTime] == loc in the following code        
        for d in defectsList: # find the min and max times
            dt_ts = op.stringToDatetime(d.detectionTime)
            rt_ts = op.stringToDatetime(d.resolutionTime)
            if minTimeVal > dt_ts and d.detectionLocationOrder == loc: 
                minTimeVal = dt_ts
            if minTimeVal > rt_ts and d.resolutionLocationOrder == loc:
                minTimeVal = rt_ts
            if maxTimeVal < dt_ts and d.detectionLocationOrder == loc: 
                maxTimeVal = dt_ts
            if maxTimeVal < rt_ts and d.resolutionLocationOrder == loc:
                maxTimeVal = rt_ts
        result = dict()
        result["max"] = op.Cast(maxTimeVal, str)
        result["min"] = op.Cast(minTimeVal, str)
        return result
    
    def normalize (self, minVal, maxVal, positionStart, positionEnd , value):
    #    print "Min: %s, Max: %s, Start: %s, End: %s, val: %s" % (minVal, maxVal, positionStart, positionEnd, value)
        op = operations.Operate()    
        if minVal is None or maxVal is None or value is None: 
            return None
        if op.Cast(positionStart, int, None) is None:
            return None
        if op.Cast(positionEnd, int, None)  is None:
            return None
        
        pf = __import__('profile')
        maxVal = op.datetimeDiffinSec(maxVal, pf.minPossibleTime)
        minVal = op.datetimeDiffinSec(minVal, pf.minPossibleTime)
        value = op.datetimeDiffinSec(value, pf.minPossibleTime)
        if maxVal == minVal:
            maxVal = maxVal + 1
        if positionEnd == positionStart:
            positionEnd = int(positionEnd) + 1
        newVal = float(value - minVal) / float(maxVal - minVal) * (int(positionEnd) - int(positionStart)) + int(positionStart)
        if int(newVal) == positionEnd :
            newVal = newVal - 1
        return int(newVal);