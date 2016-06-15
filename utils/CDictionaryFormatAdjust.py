# -*- coding: utf-8 -*-
# ##############################################################################
# class CDictionaryFormatAdjust
# Function:  Dictionary Format Adjust
#       Author:         Fan, Shuangxi (NSN - CN/Hangzhou)
#       draft:          2014-10-14 
#       modify(split):  2015-11-20
#*      description:    
# ##############################################################################
#!/usr/bin/python
import copy

# ##########################################################################
# class CDictionaryFormatAdjust
# Function:  Dictionary Format Adjust
# 1. RemoveItemByKeyPattern
# 2. AdjustFormatByKeyPattern
# 3. adjust time field, link and move to header
# - self.valueList can be single value list or content many values group
#   like: [values], or [[values],[values],...]
# - for the item being replaced, we don't delete them but indiceted by None
# ##########################################################################
class CDictionaryFormatAdjust():  
    
    def __init__(self, first, second = None): 
        if isinstance(first, dict):
            keyList = first.keys()
            valueList = first.values()
        elif isinstance(first, list) and isinstance(second, list):
            keyList = first
            valueList = second
            
        self.keyList = copy.deepcopy(keyList)
        self.valueList = []
        self.single_flag = 0
        if isinstance(valueList[0], list) == False \
           and isinstance(valueList, list) == True:
            self.single_flag = 1
            self.valueList.append(valueList)
        elif isinstance(valueList[0], list) == True:
            self.valueList = valueList

    def RemoveItemByKeyPattern(self, key_pattern): 
        for i in range(0, len(self.keyList)):
            if self.keyList[i] != None and self.keyList[i].upper().find(key_pattern.upper())>=0:
                self.keyList[i] = None


    #key_pattern = 'Ptr'
    #format_str = "0x%08x"
    def AdjustFormatByKeyPattern(self, key_pattern, format_str):
        for i in range(0, len(self.keyList)):
            if self.keyList[i] != None and self.keyList[i].upper().find(key_pattern.upper())>=0:
                for j in range(0, len(self.valueList)):
                    if self.valueList[j][i]>0:
                        self.valueList[j][i] = format_str% self.valueList[j][i]
                    else:
                        self.valueList[j][i] = '0x0'
                        
    # adjust time field, link and move to header    
    def TimeFormatAdjust(self, Time_field):
        
        Time_format = ['%04d-','%02d-','%02d,','%02d',':%02d',':%02d','.%03d']
        # field, field len
        Time_Dic = {
            'year'     : 4,
            'month'    : 2,
            'day'      : 2,
            'hour'     : 2,
            'minute'   : 2,
            'second'   : 2,
            'millisec' : 3   
        }        

        timeValueIndx_Dic = copy.deepcopy(Time_Dic)
        
        for key in timeValueIndx_Dic:
            timeValueIndx_Dic[key] = None
            
        for i in range(0, len(self.keyList)):
            if self.keyList[i] != None and timeValueIndx_Dic.has_key(self.keyList[i].strip()):        
                timeValueIndx_Dic[self.keyList[i].strip()] = i
                self.keyList[i] = None
        
        curr_Time_field  = []
        curr_Time_format = ''
        for i in range(0, len(Time_field)):
            if timeValueIndx_Dic[Time_field[i]] != None:
                curr_Time_field.append(Time_field[i])
                curr_Time_format += Time_format[i]
                
        if len(curr_Time_field):
            self.keyList.insert(0, 'TimeStamp')
        
            curr_Time_field_len = len(curr_Time_field)    
            for i in range(0, len(self.valueList)):
                curr_Time_values = copy.deepcopy(curr_Time_field)
                for j in range(0, curr_Time_field_len):
                    curr_Time_values[j] = self.valueList[i][timeValueIndx_Dic[curr_Time_field[j]]]
    
                time_str = curr_Time_format % tuple(curr_Time_values)    
                self.valueList[i].insert(0, time_str)    
  

    def get_AdjustedItems(self):
        if self.single_flag == 1:
            self.valueList = self.valueList[0]          
        return (self.keyList, self.valueList) 
    
    
    


 