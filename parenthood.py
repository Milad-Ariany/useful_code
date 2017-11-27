# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 16:31:10 2017

@author: Milad
"""
import operations
from defectProfile import defectStatus
from defectProfile import DefectProfile

class Matrix(object):
    def __init__(self):
        self.columns = None # [DefectID, ...]
        self.rows = None # [<DefectID, parenthood = [0, 1, .....]>, ...]
        self.colOrder = None
        
    def generate(self, defectsList):
        #defectsList = car.get("defects", [])
        if len(defectsList) == 0:
            return
        # Parenthood matrix represents relationship btw all errors
        # X axis represents children and Y axis represents Parents
        # SP = Start Point
        #    F1 | F2 | SP
        # F1|   |   |
        # F2|   |   |
        # order of defects in columns and rows should be the same
        # to do it, we creat a primary order of defects and keep this order in rows and columns
        op = operations.Operate()
        stat = defectStatus
        
        self.generateColumns(defectsList)
        self.rows = self.emptyRow(len(self.columns) - 1) # #rows[] length = #cols without SP  
        for cDefect in defectsList:
            if op.Cast(cDefect.status, int) == stat.multiLine.value:
                continue
            # to check parenthood, we only compare the real occurrance or detection event of a defect 
            # with other defects
            # it means if a defect has a set of inner defects, we only inspect the inner defect of that
            # which represents the real occurrance or detection of the defect
            if op.Cast(cDefect.status, int) == stat.inner.value and cDefect.occurranceIsReal == False and cDefect.detectionIsReal == False:
                continue
            
            cDefectInx = self.getColumnInx(cDefect)
            row = self.fillRow(cDefect, defectsList)
            # rows contain a list of all rows. As said, order of defects in rows and columns are the same
            # so we insert a defect's row in the it's corresponding vertical location.
            # cDefectInx shows the vertical(row) and horizontal(column) location of a defect
            self.rows[cDefectInx] = row
    
        return
    
    def fillRow(self, cDefect, defectsList):
        # Each row of the matrix shows the rel btw current defect [childDefect] and other defects [parentDefects]
        row = dict()  # <DefectID, parenthood = [0, 1, .....]>          
        parenthood = self.emptyRow(len(self.columns))
        cDefectInx = self.getColumnInx(cDefect)
        # every defect is a self-parent.
        parenthood[cDefectInx] = 1
        
        parentsIDList = self.findParents(cDefect, defectsList)
        for pDefectID in parentsIDList:
            # find the location index of pDefect in the row and set it to 1
            pDefectInx = self.getColumnInx(pDefectID)
            parenthood[pDefectInx] = 1
        # the parent of this defect is SP
        if len(parentsIDList) == 0:
            pDefectInx = self.getColumnInx("SP")
            parenthood[pDefectInx] = 1 
        row[cDefect.ID] = parenthood
        
        return row
        
    def getColumnInx(self, obj):
        if type(obj) == DefectProfile:
            return self.colOrder.get(obj.ID, None)
        return self.colOrder.get(obj, None)
        
    def generateColumns(self, defectsList):
        # order of columns is based on order of showing up
        # columnsList = [d1, d2, ...]
        # columnsDict = <Key = d1, value=orderInx = 0>
        # both represent the same order
        self.colOrder = dict()
        self.columns = []
        o = 0
        for d in defectsList:
            if d.ID not in self.colOrder: # there might be duplicated defects due to inner defects
                self.colOrder[d.ID] = o
                self.columns.append(d.ID) 
                o += 1
        self.colOrder["SP"] = o
        self.columns.append("SP")
        
        return
        
    def findParents(self, cDefect, defectsList):
        op = operations.Operate()
        # there is no paretnhood relationship btw defects after ZP6b
        cDefect_rl = op.Cast(cDefect.resolutionLine, str)
        if cDefect_rl in ["zp7", "outofline"]:
            return
        cDefect_dl = op.Cast(cDefect.detectionLine, str)
        cDefect_ol = op.Cast(cDefect.occurranceLine, str)
        cDefect_ot = op.Cast(cDefect.occurranceTakt, int)
        cDefect_dt = op.Cast(cDefect.detectionTakt, int)
        parentsList = []
        for pDefect in defectsList:
            if op.Cast(pDefect.status, int) == defectStatus.multiLine.value:
                continue
            if cDefect.ID == pDefect.ID:
                continue
            pDefect_rl = op.Cast(pDefect.resolutionLine, str)
            if pDefect_rl == cDefect_rl and pDefect_rl is not None:
                # cDefect and pDefect are resolved in the same line
                pDefect_ol = op.Cast(pDefect.occurranceLine, str)
                pDefect_dl = op.Cast(pDefect.detectionLine, str)
                pDefect_rt = op.Cast(pDefect.resolutionTakt, int)
                #print "pDefect: %s has pDefect_rl: %s and pDefect_ol: %s and pDefect_dl: %s" % (pDefect["ID, pDefect_rl, pDefect_ol, pDefect_dl)
                if cDefect_ol == pDefect_ol and pDefect_ol is not None:
                    # cDefect and pDefect are occurred in the same line
                    # So, cDefect and pDefect are took place in the same line                  
                    pDefect_ot = op.Cast(pDefect.occurranceTakt, int)
                    #print "pDefect: %s, ot=%s, rt:%s, cDefect_ot:%s)" % (pDefect.ID, pDefect_ot, pDefect_rt, cDefect_ot)                     
                    if cDefect_ot is not None and pDefect_ot is not None and pDefect_rt is not None:
                        if pDefect.resolutionIsReal == True:
                            if cDefect_ot >= pDefect_ot and cDefect_ot < pDefect_rt:
                                parentsList.append(pDefect.ID)
                        else:
                            if cDefect_ot >= pDefect_ot:
                                parentsList.append(pDefect.ID)
                elif cDefect_dl == pDefect_dl and pDefect_dl is not None:
                    # cDefect and pDefect are detected in the same line
                    # So, cDefect and pDefect are took place in the same line
                    pDefect_dt = op.Cast(pDefect.detectionTakt, int) 
                    #print "pDefect: %s, dt=%s, rt:%s, cDefect_dt:%s)" % (pDefect.ID, pDefect_dt, pDefect_rt, cDefect_dt)                                         
                    if cDefect_dt is not None and pDefect_dt is not None and pDefect_rt is not None:
                        if pDefect.resolutionIsReal == True:
                            if cDefect_dt >= pDefect_dt and cDefect_dt < pDefect_rt:
                                parentsList.append(pDefect.ID)
                        else:
                            if cDefect_dt >= pDefect_dt:# pDetect is a parent of cDefect
                                parentsList.append(pDefect.ID)
        #print "-----------------------"
        return parentsList
        
    def emptyRow(self, colLen):
        return [0] * colLen