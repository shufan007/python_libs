# -*- coding: utf-8 -*-
# ##############################################################################
# class: CSaveDataToXls 
# [Function]: save data to xls file
#       Author:         Fan, Shuangxi (NSN - CN/Hangzhou)
#       draft:          2014-10-14 
#       modify(split):  2015-11-20
#*      description: 
# ##############################################################################
#!/usr/bin/python


global XLWT_FLAG

try:
    import xlwt
    XLWT_FLAG = True
except Exception, e:
    XLWT_FLAG = False
    print"warning: %s"% e 
    
'''
# ##############################################################################
TODO:

# ##############################################################################
'''                     

# ##################################################################
# class: CSaveDataToXls 
# [Function]: save data to xls file
# [Methods]:
# * __set_styles : creat and set some styles for sheet table to choose
#      set colour, pattern, ......
#      set border for num and Item line, as well as each col
# * get_col_width: compute col width
#      adaptive col with:
#          - adjust col width accronding to item and value width
# * sort_by_itemKey: sort list values by one given item key 
# * SaveData_to_xls:  write data to .xls file
#    - fix header line
#    - return:
#       no return value, but the saved .xls file 
# ##################################################################
class CSaveDataToXls():

    def __init__(self, FileName, SheetNameList, ItemsList, DataList, sortItemKeys = []):
        self.debugLevel_1 = True
        
        if False == XLWT_FLAG:
            print "** Warning: No xlwt module! data can't save to excel table!\n"
                                 
        # judge data num
        self.data_num = len(SheetNameList)
        '''
        if isinstance(ItemsList[0], list) == False:
            self.data_num = 1
        '''        
        # ------- glob def -------------
        self.LineLetter_num = 10
        
        self.LetterWidth = 350
        self.maxWidth    = 4000
        self.minWidth    = 2000   
        self.compensationWidth = 50 
        
        #----------------------------
        self.FileName      = FileName
        self.SheetNameList = SheetNameList
        self.ItemsList     = ItemsList
        self.sortItemKeys  = sortItemKeys
        self.DataList      = DataList
                
        #   Initialize a workbook object, add a sheet,
        #   and the sheet can be overwritten
        self.wbk = xlwt.Workbook()
    
        self.eader_style = None
        self.item_style  = None
        self.data_style  = None
        
        self.__set_styles()
        self.__sort_by_itemKey()
        self.__SaveData_to_xls()    
        
    # ############################################################
    # set_styles: set and init some styles for objects to choose
    # ############################################################
    def __set_styles(self):        
        # colour style def
        colour_style0 = 'light_orange' 
        colour_style1 = 'light_blue' 
        colour_style2 = 'lime'
        colour_style3 = 'yellow'        
        
        #   ----- Seting style for excel table --------
        # set alignment        
        alignment0 = xlwt.Alignment()
        alignment0.horz = xlwt.Alignment.HORZ_CENTER  
    
        alignment1 = xlwt.Alignment()
        alignment1.horz = xlwt.Alignment.HORZ_CENTER
        alignment1.vert = xlwt.Alignment.VERT_TOP    
        alignment1.wrap = True
        
        # set borders   
        borders0 = xlwt.Borders() 
        borders0.left = 1
        #borders0.left = xlwt.Borders.DASHED 
        borders0.right = 1 
        #borders0.top = 1 
        #borders0.bottom = 1 
        borders0.left_colour =0x3A  
        borders0.right_colour=0x3A   
        
        #   Create a font to use with the style
        font0 = xlwt.Font()  
        font0.name = 'Times New Roman'
        font0.height = 0x00F0 # height.
        font0.colour_index = xlwt.Style.colour_map['blue']
        font0.bold = True
        #font0.escapement = xlwt.Font.ESCAPEMENT_SUPERSCRIPT
        font0.family = xlwt.Font.FAMILY_ROMAN
        #   Setting the background color of a cell
        
        #   Create a font to use with the style
        font1 = xlwt.Font()  
        font1.name = 'Times New Roman'
        font1.height = 0x00F0 
        font1.colour_index = xlwt.Style.colour_map['black']
        #    font1.bold = True        
        
        # set pattern
        pattern0 = xlwt.Pattern()    # Creat the pattern
        pattern0.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern0.pattern_fore_colour = xlwt.Style.colour_map[colour_style2]
        
        # set pattern
        pattern1 = xlwt.Pattern()    # Creat the pattern
        pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern1.pattern_fore_colour = xlwt.Style.colour_map[colour_style3]
           
        #   header style
        header_style = xlwt.XFStyle()
        header_style.font = font0
        header_style.alignment = alignment1
        header_style.borders = borders0 
        header_style.pattern = pattern1
        
        #   Item style
        item_style = xlwt.XFStyle()    
        item_style.font = font0
        item_style.alignment = alignment1
        item_style.borders = borders0
        item_style.pattern = pattern0   
    
        #   Data style
        data_style = xlwt.XFStyle()
        data_style.font = font1
        data_style.alignment = alignment0
        data_style.borders = borders0
        
        self.header_style = header_style
        self.item_style = item_style
        self.data_style = data_style 
        
    # ######################################################    
    # get_col_width: 
    #  - get col width accronding to item_str_len and data_str_len
    # ######################################################
    def __get_col_width(self, item_str_len, data_str_len):            
        item_width = self.LetterWidth * item_str_len
        value_width = self.LetterWidth * data_str_len
        if value_width > item_width:
            col_width = value_width            
        else:
            if item_str_len <= self.LineLetter_num:
                col_width = item_width
            elif item_width/2 > value_width:
                col_width = item_width/2                
            else: 
                col_width = value_width
        
        col_width += self.compensationWidth        
        #col_width = item_width
        '''    
        if col_width > maxWidth:
            col_width = maxWidth
        '''
        if col_width < self.minWidth:
            col_width = self.minWidth
            
        return col_width
    
    # #############################################################       
    # sort_by_itemKey: from operator import itemgetter, attrgetter
    # #############################################################
    def __sort_by_itemKey(self):
        for k in range(0, len(self.sortItemKeys)):
            itemKey = self.sortItemKeys[k]
            for i in range(0, self.data_num):
                match_indx = -1
                for j in range(0, len(self.ItemsList[i])):
                    if self.ItemsList[i][j].find(itemKey)>=0:
                        match_indx = j
                        break
                if match_indx >=0 :      
                    self.DataList[i] = sorted(self.DataList[i], key=lambda x:x[match_indx])
                    #self.DataList[i] = sorted(self.DataList[i], key=itemgetter(match_indx))

    # ######################################################
    # SaveData_to_xls: main function for data save
    # ######################################################
    def __SaveData_to_xls(self):
        if True == self.debugLevel_1:
            print "   SheetNameList: %s\n"% self.SheetNameList
       
        sheet_num = 0
        for k in range(0, self.data_num):            
             # get items and data     
            items = self.ItemsList[k]
            data = self.DataList[k] 
            sheetName = self.SheetNameList[k]
            
            if data:
                # creat a sheet
                sheet_k = self.wbk.add_sheet(sheetName, cell_overwrite_ok = False)                
                # frozen headings  
                # position: first 2 rows
                #           first 1 col
                sheet_k.panes_frozen   =  True
                sheet_k.horz_split_pos = 2
                sheet_k.vert_split_pos = 1               
                # ------- write items of the sheet   --------
                valid_col_indx = 0
                for i in range(0, len(items)):
                    if items[i] != None:                        
                        col_width = self.__get_col_width(len(items[i].strip()), len(str(data[0][i]).strip()))                        
                        sheet_k.col(valid_col_indx).width =  col_width                        
                        '''
                        print "items[i]: %s, len(items[i]): %d, col_width: %d"% \
                              (items[i].strip(), len(items[i].strip()), col_width)
                        '''
                        try:
                            sheet_k.write(0, valid_col_indx, valid_col_indx+1, self.header_style)
                            sheet_k.write(1, valid_col_indx, items[i], self.item_style)
                        except:
                            print " ** items[%d]: %s\n"% i, items[i]
                            sheet_k.write(1, valid_col_indx, items[i][1], self.item_style)
                            
                        valid_col_indx += 1                     
                # ------- write data for each item   --------                
                for i in range(1, len(data)+1):
                    valid_col_indx = 0
                    for j in range(0 ,len(items)):
                        if items[j] != None:
                            try:
                                sheet_k.write(i+1, valid_col_indx, data[i-1][j], self.data_style)
                            except:
                                sheet_k.write(i+1, valid_col_indx, '-', self.data_style)
                                
                            valid_col_indx += 1

                print "   - sheet: '%s' write success!\n"% sheetName
                sheet_num += 1                 
        try:
            self.wbk.save(self.FileName + '.xls')  # save data to .xls file 
            
        except:
            print "** Error: '%s.xls' may opending now! please close it!\n" % self.FileName

