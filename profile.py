# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 20:17:08 2017

@author: Milad
"""

import defectProfile as df
import jsonOP as json
import operations
from car import Car

globalRawDefects = r'C:\Users\Milad\Desktop\My Project\Data\output.csv'
globalJsonProfileFile = "C:\Users\Milad\Desktop\My Project\Code\ErrorProfiling\output\Profile_v8.json"
globalCsvProfileFile = "C:\Users\Milad\Desktop\My Project\Code\ErrorProfiling\output\Profile_v8.csv"
# this time should be smaller than every possible time stamp in data
# the format should be kept
minPossibleTime = "2017-01-01-00.00.01.000000"

class Profile(): 
    def __init__(self, rawDataFilePath = None, jsonFilePath = None, csvFilePath = None):
        self.jsonFile = jsonFilePath
        self.csvFile = csvFilePath
        self.rawSource = rawDataFilePath
        self.source = None
    
#    def dataFrame(self):
#        pd = __import__('pandas')
#        self.source = pd.read_csv(self.rawSource, ',')
#    
    def findSibling(self, carObj, dfObj):
        # in case that the defect has been detected and resolved once,
        # then its resolution and detection time will be the same and 
        # it contains resolution device. Then there will be only 1 corresponding row
        op = operations.Operate()
        df_dt = op.stringToDatetime(dfObj.detectionTime)
        df_rt = op.stringToDatetime(dfObj.resolutionTime)
        # this defect has no sibling in the current list of car's defects
        # add it to the current list
        if df_dt == df_rt and (dfObj.resolutionDeviceName != None or len(dfObj.resolutionDeviceName) > 0):
            self.updateCarDefects(carObj, dfObj)
        # otherwise, the defect is represeted in 2 rows
        currentDefectID = dfObj.ID
        # we check if this defect is already recorded for this car
        # if yes, its means:
        # 1. The defect is represented in 2 rows and has a sibiling 
        # 2. The defect is represented in 1 row and will be fetched itself
        for d in carObj.defects:
            if currentDefectID == op.Cast(d.ID, str):
                return d
        return False
    
    def updateCarDefects(self, carObj, dfObj):
        if type(dfObj) is list and len(dfObj) > 0:
            carObj.defects.extend(dfObj)
            return
        if type(dfObj) is df.DefectProfile():
            dfObj.rawSource = None
            carObj.defects.append(dfObj)
            return
        return
        
    def readRawData(self):
        op = operations.Operate()
#        self.dataFrame()
        self.source = op.dataFrame(self.rawSource)
        carsDict = dict()
        op = operations.Operate()
        for inxDefect in range(len(self.source)):
            row = self.source.iloc[inxDefect, ]
            dfObj = df.DefectProfile(row)
            dfObj.populate()
            carID = dfObj.carID  
            carObj = carsDict.get(carID, Car(row).populate())           
            # check if the defect is represented in 2 rows
            siblingDf = self.findSibling(carObj, dfObj)
            if siblingDf == False:
                # only record the partial defect
                self.updateCarDefects(carObj, dfObj)
            else:
                # Extend it
                # update close/open device of the sibiling defect
                self.mergeSiblings(siblingDf, dfObj)
                # set extra device related info for this defect
                siblingDf.extend()
                innerDefects = siblingDf.innerDefects()
                if len(innerDefects) != 0:
                    carObj.defects.extend(innerDefects)
                
            if carID not in carsDict:
                carObj.ID = carID
                carsDict[carID] = carObj
        return carsDict
        
    def generate(self):
        print "Started"
        carsDict = self.readRawData()
        for carID, carObj in carsDict.items():
            carObj.defectsTaktResolution()
            carObj.setDefectsParenthood()
        data = self.prepareForJSON(carsDict)
        jsonObj = json.JsonOP(self.jsonFile)
        jsonObj.write(data)
        self.csvProfileFile(carsDict)
        return
    
    def mergeSiblings(sourceDf, extentionDf):
        if sourceDf.resolutionDeviceName == None or len(sourceDf.resolutionDeviceName) < 1 : # The sourceDF has not the rel_device
            sourceDf.resolutionDeviceName = extentionDf.resolutionDeviceName
        else: # the sourceDf has not the det_device
            sourceDf.detectionDeviceName = extentionDf.detectionDeviceName
        return    
        
    def prepareForJSON(self, carsDict):
        ls = []
        for key, value in carsDict.items():
            ls.append(value)
        out = dict()
        out["data"] = ls
        return out
    
    def csvProfileFile(self, carsDict):
        csv = __import__('csv')
#        # read cars from JSON file
#        jsonObj = json.JsonOP(self.jsonFile)
#        data = jsonObj.read()
        with open(self.csvFile, 'wb') as CSV:
            # prepare the csv file for writing in a right format
            csvWriter = csv.writer(CSV, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
             # Prepare header of the csv file
            self.csvHeader(csvWriter)
            for carID, carObj in carsDict.items():
                # write the profile in the csv file
                self.csvBody(carObj, csvWriter)
        return
        
    def csvHeader(self, csvWriter):
        csvWriter.writerow(['ID','carID','status','openAfterZP6b','openAfterZP7', 'error', 
                            'occurranceLine','occurranceTakt','occurranceIsReal','occurranceLocationOrder',
                            'detectionLine','detectionTime','detectionUTime','detectionTakt','detectionIsReal',
                            'detectionLocationOrder','detectionOccuranceDistance','detectionDeviceName',
                            'detectionStationName',
                            'resolutionLine','resolutionTime','resolutionUTime','resolutionTakt','resolutionLocationOrder',
                            'resolutionDetectionDistance','resolutionOccuranceDistance',
                            'resolutionDeviceName', 'resolutionStationName', 'resolutionIsReal'])
        return
    
    def csvBody(self, carObj, csvWriter):
        if type(carObj) is not Car:
            return        
        # fill body
        for d in carObj.defects:
            csvWriter.writerow([d.ID,
                               d.carID,
                               d.status,
                               d.openAfterZP6b,
                               d.openAfterZP7,
                               d.error,
                               d.occurranceLine,
                               d.occurranceTakt,
                               d.occurranceIsReal,
                               d.occurranceLocationOrder,
                               d.detectionLine,
                               d.detectionTime,
                               d.detectionUTime,
                               d.detectionTakt,
                               d.detectionIsReal,
                               d.detectionLocationOrder,
                               d.detectionOccuranceDistance,
                               d.detectionDeviceName,
                               d.detectionStationName,
                               d.resolutionLine,
                               d.resolutionTime,
                               d.resolutionUTime,
                               d.resolutionTakt,
                               d.resolutionLocationOrder,
                               d.resolutionDetectionDistance,
                               d.resolutionOccuranceDistance,
                               d.resolutionDeviceName,
                               d.resolutionStationName,
                               d.resolutionIsReal])    
                                   
        return