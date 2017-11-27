# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 10:36:14 2017

@author: WXUS4OT
"""

import pandas as pd
import numpy as np
class ETLprocess():
    def __init__(self, csvTQ01, csvTQ19, csvTQ13, csvT01, csvT04, savePath = None):
        self.csvTQ01 = csvTQ01 # Defects
        self.csvTQ19 = csvTQ19 # Devices
        self.csvTQ13 = csvTQ13 # Verursachers
        self.csvT01 = csvT01 # Orders
        self.csvT04 = csvT04 # Status History
        self.result = None
        self.savePath = savePath
    
    def populate(self):
         # read all cars  from order table
        self.elementaryResult()
        # Add additional Status columns {F500, ...}
        self.extendColumns()
        # Read the status history of a car and assing the necessary data to the car
        self.addStatus()
        # add defects to each car
        self.addDefects()
        # add open and close device       
        self.addDevice()
        # remove duplicate rows and set close device column
        self.dimentionReduction()
        # add the Verursacher Name to each defect
        self.addVerursacher()     
        # save the result as CSV file
        self.result.to_csv(path_or_buf = self.savePath)
        return
        
    def elementaryResult(self):
        # to keep 0 before the number like: 09867653, convert KANR0 and FGSTLFD to obj
        dfT01= pd.read_csv(self.csvT01, ';', dtype={'KANR0': object, 'FGSTLFD': object})[['KANR0', 'LACKC', 'MODELL', 'MOTORKB', 
        'GETRIEBEKB', 'FGSTTM', 'FGSTPZ', 'FGSTMJ', 'FGSTWK', 'FGSTLFD', 'KDLABEL']]
        # excluse cars which are not 8v model
        dfT01 = dfT01[dfT01['KDLABEL'].str.contains('A3')]        
        dfT01.rename(columns={'KANR0': 'KANR'}, inplace = True)
        self.result = dfT01
        print "ER: %s" % (len(self.result))
        return 
        
    def addDefects(self):
        # to keep 0 before the number like: 09867653, convert KANR to obj
        # to remove floating point convert G,L,T,P to str
        dfTQ01 = pd.read_csv(self.csvTQ01, ';'
                             ,dtype={'KANR': object, 'GROUP_ID': str, 'LOC_ID': str,
                                     'TYPE_ID' : str})[['DEFECT_TS', 'KANR', 
        'GROUP_ID', 'LOC_ID', 'TYPE_ID', 'DEFECTSTATE', 'DEFECTCLOSE_TS']]
        self.result = pd.merge(self.result, dfTQ01, how='left', on='KANR')
        self.result["DEFECT_ID"] = self.result["GROUP_ID"].astype(str) + self.result["LOC_ID"].astype(str) + self.result["TYPE_ID"].astype(str)
        print "AD: %s" % (len(self.result))
        return
        
    def addDevice(self):
        dfTQ19 = pd.read_csv(self.csvTQ19, ';')[['DEFECT_TS', 'REGISTER_TS', 'GERAETENAME',
        'OWNER_ID']]
        self.result = pd.merge(self.result, dfTQ19, on='DEFECT_TS')
        print "ADV: %s" % (len(self.result))
        return
        
    def addVerursacher(self):
        dfTQ13 = pd.read_csv(self.csvTQ13, ';')[['OWNER_ID', 'OWNER_TEXT']]
        self.result = pd.merge(self.result, dfTQ13, how='left', on='OWNER_ID')
        print "AV: %s" % (len(self.result))
        return
    
    def extendColumns(self):
        sLength = len(self.result)
        cols = ['DEFECT_ID', 'F500', 'F510', 'F590', 'F600', 'G200', 'G300', 'ELFIS', 'CLOSE_DEVICE'
                , 'FLAG']
        for col in cols:
            self.result[col] = pd.Series(np.random.randn(sLength), index=self.result.index)
            if col in ["G200", "G300", "ELFIS"]:
                self.result[col] = False
            else:
                self.result[col] = None
        return
        
    def readStatusHistory(self):
        dfT04 = pd.read_csv(self.csvT04, ';', dtype={'KANR': object})[['KANR', 'STATUS0', 'MDATUM', 'MZEIT', 'LFDNR']]
        dfT04.rename(columns={'STATUS0': 'STATUS', 'LFDNR': 'partialOrder'}, inplace=True)                        
        return dfT04.loc[dfT04['STATUS'].isin(["F500", "F510", "F590", "F600", "G200", "G300"])]
   
    def addStatus(self):
        dfStatusHistory = self.readStatusHistory()
        for inxCar in range(len(self.result)):            
            car = self.result.iloc[inxCar, ]
            # get status history of a particular car
            dfTmp = dfStatusHistory.loc[dfStatusHistory['KANR'] == car['KANR']]
            if dfTmp.empty:
                continue
            # if a particular status for a car exists
            if dfTmp.loc[dfTmp['STATUS'] == "F500"].empty is False:
                # there should be one row, so we look for the first row .iloc[0, ]
                timestamp = "%s %s" % (dfTmp.loc[dfTmp['STATUS'] == "F500"].iloc[0, ]["MDATUM"],
                                       dfTmp.loc[dfTmp['STATUS'] == "F500"].iloc[0, ]["MZEIT"])
                self.result['F500'][inxCar] = timestamp
            if dfTmp.loc[dfTmp['STATUS'] == "F510"].empty is False:
                # there should be one row, so we look for the first row .iloc[0, ]
                timestamp = "%s %s" % (dfTmp.loc[dfTmp['STATUS'] == "F510"].iloc[0, ]["MDATUM"],
                                       dfTmp.loc[dfTmp['STATUS'] == "F510"].iloc[0, ]["MZEIT"])
                self.result['F510'][inxCar] = timestamp
            if dfTmp.loc[dfTmp['STATUS'] == "F590"].empty is False:
                # there should be one row, so we look for the first row .iloc[0, ]
                timestamp = "%s %s" % (dfTmp.loc[dfTmp['STATUS'] == "F590"].iloc[0, ]["MDATUM"],
                                       dfTmp.loc[dfTmp['STATUS'] == "F590"].iloc[0, ]["MZEIT"])
                self.result['F590'][inxCar] = timestamp
            if dfTmp.loc[dfTmp['STATUS'] == "F600"].empty is False:
                # there should be one row, so we look for the first row .iloc[0, ]
                timestamp = "%s %s" % (dfTmp.loc[dfTmp['STATUS'] == "F600"].iloc[0, ]["MDATUM"],
                                       dfTmp.loc[dfTmp['STATUS'] == "F600"].iloc[0, ]["MZEIT"])
                self.result['F600'][inxCar] = timestamp
            if dfTmp.loc[dfTmp['STATUS'] == "G200"].empty is False:
                self.result['G200'][inxCar] = True
            if dfTmp.loc[dfTmp['STATUS'] == "G300"].empty is False:
                self.result['G300'][inxCar] = True
        print "AS: %s" % (len(self.result))
        return
        
    def dimentionReduction(self):
        # What is the logic:
        # The DEFECT_TS and REGISTER_TS of the first entry which represents 
        # defect detection are always the same
        # the REGISTER_TS and DEFECTCLOSE_TS of the last entry which represent 
        # the defect resolution are always the same
        # the intermediate entries are replicated and contain no info
        # So, the below code mark those intermediate entries whith DELETE flag
        self.result['FLAG'] = np.where((self.result['REGISTER_TS'] != self.result['DEFECTCLOSE_TS']) & 
                                              (self.result['REGISTER_TS'] != self.result['DEFECT_TS'])
                                              , 'DELETE', None)
        # exclude the intermediate rows
        self.result = self.result.loc[~self.result['FLAG'].isin(["DELETE"])]
        # Set the close device to the captured device of the resolution row
        self.result['CLOSE_DEVICE'] = np.where((self.result['REGISTER_TS'] == self.result['DEFECTCLOSE_TS'])   
                                               , self.result['GERAETENAME'], None)
     
        self.result.rename(columns={'GERAETENAME': 'OPEN_DEVICE'}, inplace=True)
        print "RD: %s" % (len(self.result))                             
        return        
    
a = ETLprocess(r"C:\Users\Milad\Desktop\My Project\Data\tq01.csv", 
               r"C:\Users\Milad\Desktop\My Project\Data\tq19.csv",
               r"C:\Users\Milad\Desktop\My Project\Data\tq13.csv",
               r"C:\Users\Milad\Desktop\My Project\Data\t01_tmp.csv",
               r"C:\Users\Milad\Desktop\My Project\Data\t04.csv",
               r"C:\Users\Milad\Desktop\My Project\Data\output.csv")

a.populate()
