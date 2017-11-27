# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 17:03:48 2017

@author: Milad
"""

class Line(object):
    def lines(self):
        #<key: lineName, val: [lineInx, [StartTileNumber, EndTileNumber]]>
        out = dict()
        out["main"] = [1, [1, 153]]
        out["fa-mm"] = [2, [1, 35]]
        out["v"] = [3, [1, 7]]
        out["fa"] = [4, [1, 17]]
        out["fa-v"] = [5, [12, 18]]
        out["cm"] = [6, [1, 32]]
        out["mv"] = [7, [1, 7]]
        out["tm"] =  [8, [1, 23]]
        out["zp7"] =  [9, [1, 2]]
        out["outofline"] =  [10, [1, 1]]
        return out
    
    def parallelLines(self):
        # <LINE, <Inx of lines cuttd by this LINE, intersection takt of that line>>
        # <L2, [L3, 15]> : Line 2 enters Line 3 at takt 15 of Line 3
        # 0 = no path
        out = dict()
        out["main"] = [[9, 1]]
        out["fa-mm"] = [[4, 7]]
        out["v"] = [[1, 1]]
        out["fa"] = [[1, 63]]
        out["fa-v"] = [[2, 22]]
        out["cm"] = [[1, 16]]
        out["mv"] = [[1, 125]]
        out["tm"] = [[1, 137]]
        out["zp7"] = [[10, 1]]
        out["outofline"] = [[0, 0]]
        return out