# -*- coding: utf-8 -*-
# ##############################################################################
# model: CSyntaxParse,  for C language Syntax Parse, include:
#    class CEnumExtract: class for c enum extract
#    class CStructExtract: class for extract c structs
#    class CStructProcess(HexStrProcess): class for struct process, parse
#       Author:         Fan, Shuangxi (NSN - CN/Hangzhou)
#       draft:          2014-10-14 
#       modify(split):  2015-11-20
#*      description:    
# ##############################################################################
#!/usr/bin/python

import os
import copy
import re

from CHexStrProcess import *
    
'''
# ##############################################################################
TODO:
        
 performance optimization:
   - use mmap, use slicing to read from the file
   - set struct and save the structs ectected from source file
   - record the modify time of the source file 
   - flush file
   - use array to instand some list

# ##############################################################################
'''


# ##############################################################################
# class  CEnumExtract():
# [Function]:  class for c enum extract
# 
# [Methods]:
# * get_enum_dic:    get enum dic from File
#   - read source file, map the enum field to dic
#
# ############################################################################## 
class CEnumExtract:
    
    def __init__(self):
        
        pass
        
    # ##########################################################
    # get enum dic from File
    # ##########################################################
    def get_enum_dic(self, fileName):        
        enum_start_pattern  = re.compile('^typedef\s+enum\s+\w+\{?')
        enum_end_pattern    = re.compile('\}\s*\w+\s*\;')
        word_pattern        = re.compile('\d+')
        
        Out_Dic = {}
        
        if os.path.isfile(fileName):
            SrcFile = open(fileName,'r')
        else:
            print "**Error: File \"%s\" not exit! please check it."% fileName
            return
        
        Lines = SrcFile.read().splitlines()
        SrcFile.close()
        
        LineNum = len(Lines)
        match_flag = 0
   
        for i in range(0, LineNum):
            ThisLine = Lines[i].strip()

            if enum_start_pattern.search(ThisLine):
                match_flag = 1
                This_Dic = {}                
                enum_name = ThisLine.split('enum')[1].strip()
                if enum_name.rfind('{')>=0:
                    enum_name = enum_name[0: enum_name.rfind('{')]
                
            elif enum_end_pattern.search(ThisLine):
                
                match_flag = 0
                
                if not word_pattern.search(enum_name):
                    enum_name = ThisLine[ThisLine.find('}')+1: ThisLine.find(';')].strip()
                
                Out_Dic[enum_name] = This_Dic
                
            if match_flag and ThisLine.find('=')>0: 
                field_str = ThisLine.split('=')[0].strip()
                
                if ThisLine.find(',')>0:                    
                    num_str  = ThisLine.split('=')[1].split(',')[0].strip()
                else:
                    num_str   = ThisLine.split('=')[1].strip()
                    
                try:
                    num = int(num_str)
                except:
                    num = num_str

                This_Dic[num] = field_str         
                #print "This_Dic:%s"% This_Dic                
        return Out_Dic
    
  
        
# ##############################################################################
# class CStructExtract:
# [function]:  class for extract c structs
#** read structs from source files
# * get all C struct from given files
# * get unfolded struct and save them to dictionary
#
# * Input:
#   - StructFileNameList: file list that content structs and macrodefines
#   - OutFilePath: a path for put output files, such as, extructed structs
# * Output:
#   - self.struct_Dic: a dictionary maped all the unfolded structs
#                      struct name -> unfolded struct
#   - self.union_Dic: a dictionary maped all the unfolded unions
#                      union name -> unfolded union
# [Methods]: 
# * __init__: 
#   - define all kinds of reguler expression match pattern
#   - get input file data
# * add_macroDef_to_Dic: add defined macros to dictionary
# * get_Num_fromStr: get Num_from str
#** get_Field: get all fields of one struct or union
# * get_Struct_Map: Map all struct and union to dic
#   - only map sigle layer
#** get_UnfoldStruct: Unfold Struct
#   - Note:  consider the difference between struct and union !!! 
#   - for struct type only (not union type)
#   - recursion used
# * get_UnfoldStructMapbyDic: get_Unfold Struct Map by given Dic
# * get_struct_str: get struct str, for print the structs        
# * get_UnfoldStruct_str: get Unfold Struct str, for print the structs
# * print_all_MapedStructDic:
#   - main function for print unfolded struct
# ##############################################################################
class CStructExtract:
    
    def __init__(self, StructFileNameList, OutFilePath = None):
        # --------------- control paramaters---------------
        self.printLevel_1 = 0
        # -------------------------------------------------
        self.FilePath = OutFilePath
        # ---------- ** struct (union) defination identification **  ----------
        # operatior pattern
        self.Operator_pattern = re.compile('[\+\-\*\/\%]')
        self.Num_pattern  = re.compile('\d+')
                
        # Macro Defination pattern
        self.MacroDef_pattern = re.compile('^#define\s+\w+\s+\(?\(?\s*\w*\)?\(?\d+\s*\)?')
        
        #---------------- * Struct defination * -------------- 
        # All Struct pattern
        self.Struct_pattern  = re.compile('(^struct\s+\w+\{?\s*$)|(^typedef\s+struct\s+\w+\s*$)|(^typedef\s+struct\s*\{?\s*$)')
        # Struct_pattern_0: Struct pattern with name in header
        self.Struct_Name_pattern = re.compile('struct\s+\w+\{?\s*$')
        
        #---------------- * Union defination * --------------
        # All Union pattern
        self.Union_pattern  = re.compile('(^union\s+\w+\{?\s*$)|(^typedef\s+union\s+\w+\s*$)|(^typedef\s+union\s*\{?\s*$)')
        self.Union_Name_pattern = re.compile('union\s+\w+\{?\s*$')

        # Name in end pattern     
        self.EndName_pattern = re.compile('^\}\s*\w+\s*;$')
        
        # ---------- **  struct (union) field identification  ** ----------        
        # All Field pattern: 
        self.Field_pattern  = re.compile('([ui]\d+\s+\w+.*;)|((\w+\s+){1}(\w+(\[\s*\w+\s*\])?){1}\s*;)')
        
        #---------------- * number field * --------------        
        # Field_pattern_0: Number Field like: u32,i32,u16,i16,u8,i8,... 
        self.Field_Num_pattern  = re.compile('[ui]\d+\s+\w+.*;')

        # Field_pattern_0_0: Number field without array and segment
        # example:  u8  protocol;
        self.Field_Common_pattern = re.compile('[ui]\d+\s+\w+\s*;')
        
        # Field_pattern_0_1: Number array field 
        # example:  u32 tacframeBufferPtr[MAX_NR_OF_RLS]   ; 
        self.Field_NumArray_pattern = re.compile('[ui]\d+\s+\w+\s*\[\s*\w+\s*\]\s*;')
        
        # Field_pattern_0_2:  Number field with segment
        # example:   u32    TtiTraceTypeFlag    : 5 ; 
        self.Field_Segment_pattern = re.compile('[ui]\d+\s+\w+\s*:\s*\d+\s*;')

        #---------------- * struct field * --------------
        # Field_pattern_1: struct field
        self.Field_Struct_pattern   = re.compile('(\w+\s+){1}(\w+(\[\s*\w+\s*\])?){1}\s*;') 

        # Field_pattern_1_0: common struct field
        # example: STtiTraceCommonHeader traceHeader  ;
        self.Field_StructCommon_pattern = re.compile('(\w+\s+){1}(\w+\s?){1}\s*;')
        
        # Field_pattern_1_1: struct array field
        # example: STtiTraceCommonHeader traceHeader  ; 
        self.Field_StructArray_pattern  = re.compile('(\w+\s+){1}(\w+\s*\[\s*\w+\s*\]\s?){1}\s*;')        

        # num_type pattern: Number type like: u32,i32,u16,i16,u8,i8,... 
        self.NumType_pattern  = re.compile('[ui]\d+')
        
        # StructArray num pattern: STwoSlotPwr, sTwoSlotPwr_0 
        self.StructArrayNum_pattern  = re.compile('\w.*\[\d+\]')  
        
        #---------------- get input file data -----------------
        self.FileDataLines = []
        if not isinstance(StructFileNameList, list):
            StructFileNameList = [StructFileNameList]

        for i in range(0, len(StructFileNameList)):
            fileData = open(StructFileNameList[i],'r')
            thisDataLines = fileData.readlines()            
            self.FileDataLines.extend(thisDataLines)
            fileData.close()
        
        self.macroDef_Dic   = {}
        self.struct_Dic     = {}
        self.union_Dic      = {}
        
        self.search_Indx    = 0
        self.UnfoldStruct = []


    def unifyFieldByDic(self, fieldDic):
        for key in fieldDic:               
            for i in range(0, len(self.FileDataLines)):
                key_pos = self.FileDataLines[i].find(key)
                if key_pos >= 0:
                    self.FileDataLines[i] = self.FileDataLines[i][0: key_pos] + fieldDic[key]\
                                            + self.FileDataLines[i][key_pos + len(key):]

    # ######################################################
    # add_macroDef_to_Dic: add defined macros to dictionary
    # ######################################################
    def add_macroDef_to_Dic(self):
        DataLine = self.FileDataLines[self.search_Indx]
        macro_key = DataLine.split()[1]   # var name
        num_str = DataLine.split()[2]
        
        right_bracketIndx1 = num_str.find(')')
        right_bracketIndx2 = num_str.rfind(')')
        if right_bracketIndx1 >= 0:
            # like: (4)
            if right_bracketIndx1 == right_bracketIndx2:           
                bracketIndx = num_str.find('(')
                if bracketIndx >= 0:
                    num_str = num_str[bracketIndx+1: num_str.rfind(')')]                      
            else:
                # like: ((u32)16)
                num_str = num_str[right_bracketIndx1+1: right_bracketIndx2]
                
                left_bracketIndx = num_str.find('(')
                right_bracketIndx = num_str.find(')')
                
                # like: ((u32) (60))
                if left_bracketIndx>=0 and left_bracketIndx < right_bracketIndx:
                    num_str = num_str[left_bracketIndx+1: right_bracketIndx]                
        try:        
            num = int(num_str)
        except:
            # like: 0xFF
            try:
                num = int(num_str, 16)
            except:
                # like: 190/* reference
                num_str = self.Num_pattern.search(num_str).group()
                num = int(num_str)            
        self.macroDef_Dic[macro_key] = num            
        self.search_Indx += 1
        
    # ###################################################################
    # get Num_from str
    # process the str ike:
    #   MAX_NR_OF_RLS
    #   L1TRA_TAC_DMAX_NUM_HSSCCH * L1TRA_TAC_DMAX_NUM_HSSCCH
    # ###################################################################
    def get_Num_fromStr(self, Instr):
        try:
            num = int(Instr)
        except:            
            m = self.Operator_pattern.search(Instr)            
            if m:
                macroNums = self.Operator_pattern.split(Instr)
                num_str0 = str(self.macroDef_Dic[macroNums[0]])
                num_str1 = str(self.macroDef_Dic[macroNums[1]])
                Operator = m.group()
                num = eval(num_str0 + Operator + num_str1)             
            elif Instr in self.macroDef_Dic:                            
                num = self.macroDef_Dic[Instr] 
            else: 
                #print "\n** macroDef: '%s' not find, please check it!"% Instr
                num = None                              
        return num                
                
    # ###################################################################
    # get all fields of one struct or union
    # ###################################################################
    def get_Field(self, var_name):        
        FieldList = []        
        while True:            
            DataLine = self.FileDataLines[self.search_Indx]                    
            if DataLine.find(r'//')<0 and self.Field_pattern.search(DataLine):
                if self.Field_Num_pattern.search(DataLine):
                    if self.Field_Common_pattern.search(DataLine):
                        m = self.Field_Common_pattern.search(DataLine)
                        field_str_list = m.group()[0:-1].split()
                        field_name = field_str_list[-1]                        
                        field_type = field_str_list[-2]
                        field_len = int(field_type[1:])                        
                        FieldList.append([field_type, field_name, field_len])
                    elif self.Field_NumArray_pattern.search(DataLine):
                        m = self.Field_NumArray_pattern.search(DataLine)
                        field_str_list = m.group()[0:-1].split()
                        field_name = field_str_list[-1]                        
                        field_type = field_str_list[-2]                        
                        field_len = int(field_type[1:])
                        field_num_str = field_name[field_name.rfind('[')+1:field_name.rfind(']')].strip()                        
                        field_num = self.get_Num_fromStr(field_num_str)                               
                        field_name = field_name[0:field_name.rfind('[')] 
                        if field_num != None:
                            for i in range(0, field_num):
                                field_name_i = "%s[%d]"% (field_name,i)
                                FieldList.append([field_type, field_name_i, field_len])
                    elif self.Field_Segment_pattern.search(DataLine):
                        m = self.Field_Segment_pattern.search(DataLine)
                        field_str_list = m.group()[0:-1].split(':')
                        field_name = field_str_list[0].split()[-1]                        
                        field_type = field_str_list[0].split()[-2]                        
                        field_len = int(field_str_list[1].strip())                        
                        FieldList.append([field_type, field_name, field_len])                    
                elif self.Field_Struct_pattern.search(DataLine):
                    if self.Field_StructCommon_pattern.search(DataLine):
                        m = self.Field_Struct_pattern.search(DataLine)
                        field_str_list = m.group()[0:-1].split()
                        field_name = field_str_list[-1]                        
                        field_type = field_str_list[-2]                                               
                        FieldList.append([field_type, field_name])
                    elif self.Field_StructArray_pattern.search(DataLine):
                        m = self.Field_StructArray_pattern.search(DataLine)
                        field_str_list = m.group()[0:-1].split()
                        field_name = field_str_list[-1]                        
                        field_type = field_str_list[-2]
                        field_num_str = field_name[field_name.rfind('[')+1:field_name.rfind(']')].strip()
                        field_num = self.get_Num_fromStr(field_num_str)
                                
                        field_name = field_name[0:field_name.rfind('[')] 
                        if field_num != None:
                            for i in range(0,field_num):
                                field_name_i = "%s[%d]"% (field_name, i)
                                FieldList.append([field_type, field_name_i])
            elif DataLine.find('}')>=0:
                if var_name == None:
                    m = self.EndName_pattern.search(DataLine)
                    try:
                        var_name = m.group()[1:-1].strip()
                        #var_name = m.group().split('}')[1].split(';')[0].strip()
                    except:
                        print "** critical: EndName_pattern not find! search_Indx: %d\n"% self.search_Indx+1
                        exit(1)                        
                self.search_Indx += 1                
                break           
            self.search_Indx += 1
            
        return (var_name, FieldList)

    # ###################################################################    
    # Map all struct and union to dic
    # only map sigle layer
    # ###################################################################
    def get_Struct_Map(self):        
        while self.search_Indx < len(self.FileDataLines):               
            DataLine = self.FileDataLines[self.search_Indx]
            var_name  = None            
            if self.MacroDef_pattern.search(DataLine):
                self.add_macroDef_to_Dic()                
            elif self.Struct_pattern.search(DataLine):                   
                # struct name in the head
                if self.Struct_Name_pattern.search(DataLine):                
                    var_name = DataLine.split('struct')[1].strip()
                self.search_Indx += 1                    
                (var_name, FieldList) = self.get_Field(var_name)                                    
                self.struct_Dic[var_name] = FieldList
            elif self.Union_pattern.search(DataLine):                  
                # struct name in the head
                if self.Union_Name_pattern.search(DataLine):                
                    var_name = DataLine.split('union')[1].strip()
                self.search_Indx += 1                    
                (var_name, FieldList) = self.get_Field(var_name)                                    
                self.union_Dic[var_name] = FieldList
            else:    
                self.search_Indx += 1    

    # ###################################################################
    # Note:  consider the difference between struct and union !!! 
    # for struct type only (not union type)
    # recursion used
    # input var self.UnfoldStruct = [] is needed
    # StructName: input struct name
    # fieldName_add_str: if number contion field name, we should indenfy the number
    #   such as, STwoSlotPwr, sTwoSlotPwr_0
    # ###################################################################
    def get_UnfoldStruct(self, StructName, fieldName_add_str = ''):
        
        try:
            StructList = self.struct_Dic[StructName]
        except:
            print "** Warning: Struct Name: '%s' not find in Struct map Dic!\n"% StructName
            #print "   May be the struct not include in file!\n"
            StructList = []
        
        fieldName_add_str0 = fieldName_add_str    
        for i in range(0, len(StructList)):
            field_type = StructList[i][0]
            field_name = fieldName_add_str0 + StructList[i][1]
            
            if self.NumType_pattern.match(field_type):
                self.UnfoldStruct.append([field_type, field_name, StructList[i][2]])
            else:
                if self.StructArrayNum_pattern.match(StructList[i][1]):                    
                    fieldName_add_str = fieldName_add_str0 + (StructList[i][1] + '.')
                else:
                    fieldName_add_str = fieldName_add_str0

                self.get_UnfoldStruct(field_type, fieldName_add_str)

    # ######################################################
    # get_Unfold Struct Map by given Dic
    # ######################################################
    def get_UnfoldStructMapbyDic(self, Struct_Map_Dic):
        OutStructDic = {}
        for key in Struct_Map_Dic:            
            StructName = Struct_Map_Dic[key]
            if StructName != None:            
                # print " - Struct Name: %s"% StructName                           
                self.UnfoldStruct = []
                self.get_UnfoldStruct(StructName)
                OutStructDic[StructName] = self.UnfoldStruct        
        return OutStructDic

    # ############################################################
    # for print the structs being geted
    # ######################################################
    
    def get_struct_str(self, StructList, out_str):
        for j in range(0,len(StructList)):
            if len(StructList[j]) == 3:
                out_str += '        %s, %s, %d\n'% (StructList[j][0], StructList[j][1], StructList[j][2])
            else:
                out_str += '        %s, %s\n'% (StructList[j][0], StructList[j][1])                
        return out_str

    def get_UnfoldStruct_str(self, Struct_Map_Dic):
        OutStruct_Map_Dic = self.get_UnfoldStructMapbyDic(Struct_Map_Dic)
        out_str = ''
        for key in OutStruct_Map_Dic:            
            if key != None:                
                if self.printLevel_1 == 1:
                    print " - Struct Name: %s"% key 
                    
                out_str += ' * Struct: %s\n'% (key)            
            out_str = self.get_struct_str(OutStruct_Map_Dic[key], out_str)
        return out_str
    
    def print_MapedStructDic(self, structDicList):
        self.get_Struct_Map()
       
        out_str = '\n********* All Maped Struct **********\n'
        i = 0
        for key in self.struct_Dic:
            out_str += ' * Struct[%d]: %s\n'% (i,key)
            i += 1
            out_str = self.get_struct_str(self.struct_Dic[key], out_str)                   
        
        out_str += '\n********* All Maped Union **********\n'
        i = 0
        for key in self.union_Dic:
            out_str += ' * Union[%d]: %s\n'% (i,key)
            i += 1
            out_str = self.get_struct_str(self.union_Dic[key], out_str)

        OutFile = open(os.path.join(self.FilePath,'StructMapDic.txt'),'w')
        OutFile.write(out_str)
        OutFile.close()

        for i in range(0, len(structDicList)):
            out_str = '\n******************************************\n'
            out_str += self.get_UnfoldStruct_str(structDicList[i])       

        OutFile = open(os.path.join(self.FilePath,'UnfoldStruct.txt'),'w')
        OutFile.write(out_str)
        OutFile.close()                                
            
# ##############################################################################
# class CStructProcess(HexStrProcess):
# [Function]:  class for struct process, parse
# * the struct format must be like:             
#   struct = [
#        ['u32', 'field_str1',    4 ],
#        ['u32', 'field_str2',    12 ],
#        ['u32', 'field_str3',    16 ],
#              ......
#        ['u32', 'field_strn',    32 ]
#    ] 
# [Methods]:
#** get_u32SegmentFromStruct:
#   - get u32 segment list from struct in 32 bite aligning
#** get_UnionAlignedSegment: get Union Aligned Segment
#
# * get_StructValues:  get all segment values from data
#                      accronding to struct and segment list
# * get_LastStructSegmentValueFromData: get the last segment value of struct from data
#   - this value may used to judge something
# * get_Items_from_Struct: get items from struct
# ##############################################################################
class CStructProcess():
    
    def __init__(self):
        
        self.hexStr_obj = CHexStrProcess()
    
    # #############################################################        
    # get u32 segment list from struct in 32 bite aligning 
    # #############################################################
    def get_u32SegmentFromStruct(self, Struct):
        u32_len = 32
        SegmentList = []
        tempList = []
        Temp_sum = 0
        for i in range(0,len(Struct)):
            try:
                thisNum = int(Struct[i][2])
            except:
                print "**Warning: Struct[%d][2]: %s\n"% i, Struct[i][2]
                
            if Temp_sum + thisNum == u32_len:
                tempList.append(thisNum)                
                SegmentList.append(tempList)                
                tempList = []
                Temp_sum = 0                
            elif Temp_sum + thisNum > u32_len:
                SegmentList.append(tempList)               
                tempList =  [thisNum]
                Temp_sum =  thisNum
            elif Temp_sum + thisNum < u32_len:
                tempList.append(thisNum)
                Temp_sum += thisNum            
        if Temp_sum > 0 and Temp_sum <= u32_len:
            SegmentList.append(tempList)
            
        return SegmentList

    # ###############################################################################
    # function: get Union Aligned Segment
    # * For small union field, padding the residue part
    # * For padded u32 part, Note it as '[None]'
    #   Segments[0] is all [None] list to indicate should skip number of u32 in data
    #   like: [[None],[None],...]
    # - input:
    #    [1]. All_Union_Dic : all the union that have maped to dictionary
    #    [2]. All_Struct_Dic: all the struct that have maped to dictionary
    #    [3]. UnionName:  the name of the union that should be unfolded
    #         and get its AlignedSegments
    # - output:
    #    [1]. AlignedSegments: Aligned Segments of the unfolded union 
    # ###############################################################################
    def get_UnionAlignedSegment(self, All_Union_Dic, All_Struct_Dic, UnionName):        
        UnionList = []
        for i in range(0, len(All_Union_Dic[UnionName])):        
            UnionList.append(All_Union_Dic[UnionName][i][0])

        union_len = 0
        Segments  = []
        for i in range(0, len(UnionList)):
            Struct = All_Struct_Dic[UnionList[i]]
            SegmentList = self.get_u32SegmentFromStruct(Struct)
            Segments.append(SegmentList)
            
            if len(SegmentList) > union_len:
                union_len = len(SegmentList)
                
        AllNoneSegment  = []
        for i in range(0, union_len):
            AllNoneSegment.append([None])

        AlignedSegments = []
        AlignedSegments.append(AllNoneSegment)        
        AlignedSegments.extend(Segments)
        for i in range(0, len(UnionList)):            
            if len(Segments[i]) < union_len:
                for j in range(0, union_len - len(Segments[i])):
                    AlignedSegments[i+1].append([None])       
        return AlignedSegments
        
    # ###################################################################
    # get all segment values from data
    # accronding to struct and segment list
    # SegmentList may not have the same length as Struct
    # ###################################################################
    def get_StructValues(self, Data, Struct, SegmentList = None):        
        if SegmentList == None:
            SegmentList = self.get_u32SegmentFromStruct(Struct)
        #print "SegmentList: %s"% SegmentList
        #time.sleep(1)
        Values = []
        structField_Indx = 0

        for i in range(0,len(SegmentList)):
            if SegmentList[i][0] != None:
                value = self.hexStr_obj.word_split(Data[i], SegmentList[i], 'Little')
                #print value
                for j in range(0, len(value)):
                    bit_len = int(Struct[structField_Indx + j][0][1:])
                    if Struct[structField_Indx + j][0][0] == 'i': 
                    #if Struct[structField_Indx + j][0][0] == 'i' or bit_len == 32:
                        value[j] = self.hexStr_obj.SignedIntConvert(value[j], bit_len)
                Values.extend(value)
                structField_Indx += j            
        return Values    

    # ###################################################################
    # get the last segment value of struct from data
    # this value may used to judge something
    # ###################################################################
    def get_LastStructSegmentValueFromData(self, Data, Struct, SegmentList = None):        
        if SegmentList == None:
            SegmentList = self.get_u32SegmentFromStruct(Struct)
            
        data_indx = len(SegmentList)-1
        value = self.hexStr_obj.word_split(Data[data_indx], SegmentList[-1], 'Little')
        
        lastSegment = SegmentList[-1]
        lastValue = value[-1]
        return (data_indx, lastSegment, lastValue)   
    
    # get items from struct        
    def get_Items_from_Struct(self, Struct):
        Items = []
        for i in range(0,len(Struct)):
            Items.append(Struct[i][1])
        return Items    
