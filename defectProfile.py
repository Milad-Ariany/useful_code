# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 16:53:36 2017

@author: Milad
"""

from enum import Enum
import operations as operations
import defect as dfct
import SDGL as sdgl
import line as ln

class defectStatus(Enum):
    oneLine = 0
    inner = 1
    multiLine = 2
    
class DefectProfile(dfct.DefectSpec): 
    def __init__(self, rawData = None):
        self.ID = None # ID recorded in DataLake for a defect
        self.carID = None
        self.status = None # 0 = SoloDefect, 1 = InnerDefect, 2 = sourceOfInnerDefect
        self.occurranceLine = None
        self.occurranceTakt = None
        self.occurranceIsReal = False
        self.occurranceLocationOrder = None
        self.detectionLine = None
        self.detectionTime = None
        self.detectionUTime = None
        self.detectionTakt = None
        self.detectionIsReal = False
        self.detectionLocationOrder = None
        self.detectionOccuranceDistance = None
        self.detectionDeviceName = None
        self.detectionStationName = None
        self.resolutionLine = None
        self.resolutionTime = None
        self.resolutionUTime = None
        self.resolutionTakt = None
        self.resolutionLocationOrder = None
        self.resolutionDetectionDistance = None
        self.resolutionOccuranceDistance = None       
        self.resolutionDeviceName = None
        self.resolutionStationName = None
        self.resolutionIsReal = False
        self.openAfterZP6b = False
        self.resolvedInZP7 = False
        self.abnormal = False
        self.error = None
        self.rawSource = rawData

#    def dataFrame(self, filePath):
#        pd = __import__('pandas')
#        out = pd.read_csv(filePath, ';')
#        return out
        
    def populate(self):
        op = operations.Operate()
        self.carID = op.Cast(self.rawSource['KANR'], str)
        self.ID = op.Cast(self.rawSource['DEFECT_ID'], str)
        self.detectionTime = self.rawSource['DEFECT_TS']
        self.resolutionTime = self.rawSource['REGISTER_TS']
        self.detectionDeviceName = self.rawSource['OPEN_DEVICE']          
        self.resolutionDeviceName = self.rawSource['CLOSE_DEVICE']
        self.groupID = self.rawSource['GROUP_ID']
        self.locationID = self.rawSource['LOC_ID']  
        self.typeID = self.rawSource['TYPE_ID']  
        self.verursacher = self.rawSource['OWNER_TEXT']      
        return
    
    def extend(self):
        self.setDeviceRelatedData()
        self.setGroupRelatedData()
        return
    
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
     
    def setGroupRelatedData(self):
        GpDict = self.fetchSDGL("g")
        GpObj = GpDict.get(self.verursacher, sdgl.StationDeviceGroupLocation())
        self.occurranceLine = GpObj.line
        self.occurranceTakt = GpObj.lastTakt
        self.occurranceLocationOrder = GpObj.locationOrder
        return
            
    def setDeviceRelatedData(self):
        op = operations.Operate()
        DvDict = self.fetchSDGL("d")
        DvObj = None
        # Detection device----------------
        # fetch required data from corresponding device profile 
        if self.detectionDeviceName in DvDict:
            # it is detected before the end of line
            DvObj = DvDict.get(self.detectionDeviceName, sdgl.StationDeviceGroupLocation()) 
        else:
            # it is not detected by the end of line
            DvObj = DvDict.get(sdgl.oufOfLineStationDeviceGroupID, sdgl.StationDeviceGroupLocation())        
        self.detectionLine = DvObj.line
        self.detectionDeviceName = DvObj.deviceName 
        self.detectionStationName = DvObj.stationName
        self.detectionLocationOrder = DvObj.locationOrder
        # Resolution device----------------
        # check if the error is open after ZP6b
        if self.resolutionDeviceName in DvDict:
            # it is resolved by the end of line
            # fetch required data from corresponding device profile 
            DvObj = DvDict.get(self.resolutionDeviceName, sdgl.StationDeviceGroupLocation())
        else:
            DvObj = DvDict.get(sdgl.oufOfLineStationDeviceGroupID, sdgl.StationDeviceGroupLocation())        
        self.resolutionLine = DvObj.line
        self.resolutionDeviceName = DvObj.deviceName
        self.resolutionStationName = DvObj.stationName
        self.resolutionLocationOrder = DvObj.locationOrder
        # error is resolved before it has been detected
        if op.Cast(self.resolutionLocationOrder, int) < op.Cast(self.detectionLocationOrder, int):
            self.abnormal = True
        if op.Cast(self.resolutionLocationOrder, int) >= 900: # loc 900 is beginning of ZP7
               self.openAfterZP6b = True
               if op.Cast(self.resolutionLocationOrder, int) < 1000: # loc 1000 is after ZP7
                   self.resolvedInZP7 = True
        return
        
    def innerDefects(self):
        #    print "defect: %s is reported for breaking down. OL:%s, DL: %s, RL: %s" % (defect.ID, defect.occurranceLine, defect.detectionLine, defect.resolutionLine)
        generatedDefects = []
        # The life cycle of a defect is Occ --> Res or Det --> Res
        if self.occurranceLine != None and self.resolutionLine != None:
            if self.occurranceLine != self.resolutionLine:
                    # path[Occ_Line, inner_Line1, ..., Res_line]
                    # Each pairs of path[i] and path[i+1] are immidiate neighbors
                    # a defect should be duplicated from a specific takt from Occurance line 
                    # to a specific takt in Resolution line. It means:
                    # if path[occ_line(l2, occ_takt:12, intersection_start_takt: 15), 
                    #         inner_line(l3,intersection_start_takt:4, intersection_leaving_takt:9),
                    #         res_line(l4, intersection_start_takt:8, occ_takt: 12)]
                    # then, we have 3 duplications with following info:
                    # d1: (occ&res)line:2, occ_takt: 12, res_takt: 15
                    # d2: (occ&res)line:3, occ_takt: 4, res_takt: 9
                    # d3: (occ&res)line:4, occ_takt: 8, res_takt: 12
        #            print "Occ --> Res for defect %s" % (defect.ID)
                path = self.findPathBtwLines(self.occurranceLine, self.resolutionLine, [self.occurranceLine])
                if path == None:
                    return
        #            print "Path from occ to res: ", path
                coordination = self.findCoordinations(path)
        #           print coordination
                generatedDefects = self.generateInnerDefects("occ", path, coordination)
        elif self.detectionLine != None and self.resolutionLine != None:
            if self.detectionLine != self.resolutionLine:
                # path[Det_Line, inner_Line1, ..., Res_line]
        #            print "Det --> Res for defect %s" % (defect.ID)
                path = self.findPathBtwLines(self.detectionLine, self.resolutionLine, [self.detectionLine])
                if path == None:
                    return
        #            print "Path from det to res: ", path
                coordination = self.findCoordinations(path)
                generatedDefects = self.generateInnerDefects("det", path, coordination)
        #    if len(generatedDefects) > 0:
        #        print "%s inner defects are generated for defect: %s" % (len(generatedDefects), defect.ID)
        #        print "------------------"
        stat = defectStatus
        if len(generatedDefects) == 0:
            self.status = stat.oneLine.value
            self.detectionIsReal = True
            self.occurranceIsReal = True
            self.resolutionIsReal = True
        else:
            self.status = stat.multiLine.value
            
        return generatedDefects   
        
    def findCoordinations(self, path):
        coordination = []
        for inx, lineName in enumerate(path):
            # inx = 0 is the occ line
            # inx = len(path) - 1 is the res line
            # others are inner lines
            if inx + 1 < len(path):
                result = self.linesIntersectionResolution(lineName, path[inx + 1])
                if result == None:
                    self.error = self.error + "**\line cannot be resolved" if self.error != None else "**\line cannot be resolved"
                else:
                    coordination.extend(result)
        return coordination
    
    def findPathBtwLines(self, source, dest, Path):
        #    print "funcFindPathBtwLines %s and %s" % (source, dest)
        #the path from source to destination is found
        if source == dest:
            return Path
        linesDict = ln.Line().lines()    
        parallelLinesIntersectionDict = ln.Line().parallelLines()
        # paths[[], ...]    
        paths = parallelLinesIntersectionDict.get(source, [])
        for line in paths:
            # line[0] = line index
            # line[1] = intersection takt
            if line[0] != 0:
                lineName = ""
                # linesDict: <key: lineName, val: [lineInx, [StartTileNumber, EndTileNumber]]>
                for key, val in linesDict.iteritems():
                    if line[0] == val[0]:
                        lineName = key
                        break
                Path.append(lineName)
                return self.findPathBtwLines(lineName, dest, Path)     
        return
    
    def generateInnerDefects(self, startFlag, path, coordinations):
        # path[Line1, Line2, ..., LineX]
        # coords[[L1_start, L1_last], ..., [Lx_start, Lx_last]]
        if coordinations == None or len(coordinations) == 0 or path == None or len(path) == 0:
            return []
            
        # inner defects will be generated till ZP6b
        if "zp7" in path:
            path.remove("zp7")
        if "outofline" in path:
            path.remove("outofline")
            
        defects = []
        stat = defectStatus
        for inx, line in enumerate(path):
            newDefect = DefectProfile()
            newDefect.ID = self.ID
            newDefect.carID = self.carID
            newDefect.groupID = self.groupID
            newDefect.locationID = self.locationID
            newDefect.typeID = self.typeID
            newDefect.status = stat.inner.value
            
            if startFlag == "occ":
                newDefect.occurranceLine = line
                newDefect.occurranceTakt = coordinations[inx][0]
                # valid recorded info of occurance should be copied to the corresponding generated defect
                if inx == 0:
                    newDefect.occurranceLocationOrder = self.occurranceLocationOrder
                    newDefect.occurranceIsReal = True
            elif startFlag == "det":
                newDefect.detectionLine = line
                newDefect.detectionTakt = coordinations[inx][0]
                # valid recorded info of detection should be copied to the corresponding generated defect
                if inx == 0:
                    newDefect.detectionIsReal = True
                    newDefect.detectionDeviceName = self.detectionDeviceName
                    newDefect.detectionLocationOrder = self.detectionLocationOrder
                    newDefect.detectionOccuranceDistance = self.detectionOccuranceDistance
                    newDefect.detectionStationName = self.detectionStationName
                    newDefect.detectionTime = self.detectionTime
                    newDefect.detectionUTime = self.detectionUTime
            newDefect.resolutionLine = line
            newDefect.resolutionTakt = coordinations[inx][1]
            # valid recorded info of resolution should be copied to the corresponding generated defect
            if inx == len(path) - 1:
                newDefect.resolutionDeviceName = self.resolutionDeviceName
                newDefect.resolutionLocationOrder = self.resolutionLocationOrder
                newDefect.resolutionOccuranceDistance = self.resolutionOccuranceDistance
                newDefect.resolutionStationName = self.resolutionStationName
                newDefect.resolutionTime = self.resolutionTime
                newDefect.resolutionUTime = self.resolutionUTime
                newDefect.resolutionIsReal = True
            defects.append(newDefect)
        return defects
        
    def linesIntersectionResolution(self, startLineName, destLineName):
    #    print "funcLinesIntersectionResolution(sl: %s, dl: %s)" % (startLineName, destLineName)
        destLineIntersectionTaktNumber = 0 # start line enters dest line in this takt of dest line
        destLineEndTakt = 0
        startLineEndTakt = 0
        
        linesDict = ln.Line().lines()
        lineInfo = linesDict.get(startLineName, None)
        if lineInfo == None:
            print "funcLinesIntersectionResolution error"
            return None
        startLineEndTakt = lineInfo[1][1]
        lineInfo = linesDict.get(destLineName, None)
        if lineInfo == None:
            print "funcLinesIntersectionResolution error"
            return None
        # if the dest line is the res line, then we assign the res takt to the destLineEndTakt
        # otherwise the last takt of dest line will be assigned to destLineEndTakt
        if self.resolutionLine == destLineName:
            destLineEndTakt = self.resolutionTakt
        else:    
            destLineEndTakt = lineInfo[1][1]
        parallelLinesIntersectionDict = ln.Line().parallelLines()
        destLineInx = lineInfo[0]
        intersectionLines = parallelLinesIntersectionDict.get(startLineName, [])
        for line in intersectionLines:
            # line[0] = line index
            # line[1] = intersection takt
            if line[0] == destLineInx:
                destLineIntersectionTaktNumber = line[1]
        # if the start line is either Det line or Occ line, then return calculated
        # info for start line and dest line
        # otherwise, return the info for dest line    
        if self.occurranceLine == startLineName:
            return [[self.occurranceTakt, startLineEndTakt], [destLineIntersectionTaktNumber, destLineEndTakt]]
        elif self.occurranceLine == None and self.detectionLine == startLineName:
            return [[self.detectionTakt, startLineEndTakt], [destLineIntersectionTaktNumber, destLineEndTakt]]
        else:
            return [[destLineIntersectionTaktNumber, destLineEndTakt]]
        return None
        