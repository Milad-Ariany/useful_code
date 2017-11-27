# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 16:22:35 2017

@author: Milad
"""

import profile as pf
import uparenthood as ph
import operator
#import defectProfile as dp

#p = pf.Profile()
#p = pf.Profile(pf.globalRawDefects, pf.globalJsonProfileFile, pf.globalCsvProfileFile)
#p.generate()


up = ph.Uparenthood("C:\Users\\Milad\Desktop\My Project\Code\ErrorProfiling\output\Profile_v8.json")
up.populate()

sorted_cols = sorted(up.cols.items(), key=operator.itemgetter(1))
aa = "   "
for k in sorted_cols:
    aa = aa + " " + k[0]
print aa
for k,v in up.rows.items():
    print k, v