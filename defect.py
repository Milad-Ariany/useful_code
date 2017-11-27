# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 15:28:27 2017

@author: Milad
"""
import operations

globalRawDefectKeysRelationship = r'C:\Users\Milad\Desktop\My Project\Data\Fetched\csv\CarDefect_Defect_Relationship.csv'
globalRawDefectSpec = r'C:\Users\Milad\Desktop\My Project\Data\Fetched\csv\Defects.csv'

class DefectSpec(object): 
    def __init__(self, rawData = None):
        self.uniqueID = None # Unique id which is combination of GID + LID + TID
        self.groupID = None
        self.locationID = None
        self.typeID = None
        self.verursacher = None
        self.rawSource = rawData
        
    def populate(self):
        op = operations.Operate()
        self.uniqueID = op.Cast(self.rawSource['Unique_ID_Combination'], str)
        self.groupID = op.Cast(self.rawSource['Objektgruppe_ID'], str)
        self.locationID = op.Cast(self.rawSource['Fehlerobjekt - location_ID'], str)
        self.typeID = op.Cast(self.rawSource['Fehlerart - type_ID'], str)
        self.verursacher = op.Cast(self.rawSource['Verursacher'], str)
        return

class DefectKeysRelationship(object):
    def __init__(self, filePath = None):
        self.rawSource = filePath
        self.source = None
        
    def dataFrame(self):
        pd = __import__('pandas')
        self.source = pd.read_csv(self.rawSource, ',')
        
    def populate(self):
        op = operations.Operate()
        self.source = op.dataFrame(self.rawSource)
#        self.dataFrame()
        out = dict()
        op = operations.Operate()
        for inx in range(len(self.source)):
            defectID = op.Cast(self.source['defectid'].iloc[inx,], str)
            if defectID not in out:
                out[defectID] = op.Cast(self.source['Unique_ID'].iloc[inx,], str)
        return out