# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 16:19:31 2017

@author: Milad
"""
import jsonOP as json

class Uparenthood(object):
    def __init__(self, filePath):
        self.lenCol = None
        self.lenRow = None
        self.cols = None
        self.rows = None
        self.rawSource = filePath
        self.source = None
        
    def populate(self):
        self.source = json.JsonOP(self.rawSource).read()
        cols = self.allColumns()
        rows = dict() # <Defect, [0, 1, ...]>
        for obj in self.source["data"]:
            # Each parenthood (PH) in rows points to an item in cols with the same order
            # e.g: The 3d 0 for Defect 1 points to the 3d Defect of cols
            localRows = self.readRows(obj) # List of Dicts with only one key {<"DefectID", [0, 0, 1, ...]>}            
            localCols = self.singleProfileColumns(obj) # List ["DefectID", "DID", ...]
#            print localCols
#            print localRows
#            print "------------"
            newRow = self.emptyRow()
            # iterate on all rows of one parenthood matrix
            for row in localRows:
                newRow = self.emptyRow()
                for defID, defPH in row.iteritems():
                    if defID in rows:
                        newRow = rows.get(defID)
                    for inx, val in enumerate(defPH):
                        parent = localCols[inx] # Get the DefectID with this inx 
                        parentUInx = cols.get(parent, None) # Get Uinx of this defectID in the UCols
                        if parentUInx is None:
                            continue
                        newRow[parentUInx] += val                        
                    rows[defID] = newRow       
        self.rows = rows
        self.cols = cols            
        return
        
    def allColumns(self):  
        cols = []
        for obj in self.source["data"]:
            cols = self.singleProfileColumns(obj, cols)       
        colsInx = self.listToOrderedDict(cols)      
        self.lenCol = len(cols)
        return colsInx
    
    def listToOrderedDict(self, ls):
        if type(ls) is not list:
            return dict() 
            
        out = dict()
        inx = 0
        for item in ls:
            out[item] = inx
            inx += 1        
        return out
        
    def singleProfileColumns(self, obj, columns = None):
        if type(obj) is not dict:
            return
        
        ph = obj.get("defectsParenthood", [])
        if len(ph) == 0:
            return
        
        ph = ph[0]
        if type(ph) is not dict:
            return
        
        if columns is None or type(columns) is not list:
            columns = []
    
        cols = ph.get("columns", [])
        for c in cols:
            if c in columns:
                continue
            columns.append(c)
    
        return columns
    
    def readRows(self, obj):
        if type(obj) is not dict:
            return
        
        ph = obj.get("defectsParenthood", [])
        if len(ph) == 0:
            return
        
        ph = ph[0]
        if type(ph) is not dict:
            return
               
        rows = ph.get("rows", [])
        if len(rows) == 0:
            return
        
        ls = []
        for row in rows:
            ls.append(row)
    
        return ls
        
    def emptyRow(self):
        return [0] * self.lenCol