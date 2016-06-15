# -*- coding: utf-8 -*-
# ##############################################################################
# class  CBinDataConvert
#       Function:       class for .bin and hex file convert
#       Author:         Fan, Shuangxi (NSN - CN/Hangzhou)
#       draft:          2014-10-14 
#       modify(split):  2015-11-20
#*      description:    
# ##############################################################################
#!/usr/bin/python

import struct

from CHexStrProcess import *
    
'''
# ##############################################################################
TODO:

performance optimization:
   - speed the way of unpack .bin file
* use thread for unpack .bin and parse 

# ##############################################################################
'''
    
# ##############################################################################
# class  CBinDataConvert(CHexStrProcess):
# [Function]:      class for .bin and hex file convert
#
# [Methods]:
# * Byte_to_hex: convert Byte to hex str
#
# * __u32_unpack: unpack bit stream
#   - convert u32(4 Byte) to hex str 
# * Hex_to_Bin: Convert hex file to bin file.
#
# * Bin_to_Hex: convert bin file to hex file.
#
# ##############################################################################
class CBinDataConvert():
    
    def __init__(self):
        self.hexStr_obj = CHexStrProcess()
        
    
    # ##########################################################
    # convert Byte to hex str
    # ##########################################################
    def Byte_to_hex(self, Byte_data):
        hex_data = ''
        for i in range(0,len(Byte_data)):
            temp = ord(Byte_data[i])
            temp = "%02x"% temp            
            hex_data += temp 
            
        return hex_data

    # #####################################################
    # unpack bit stream: 
    # convert u32(4 Byte) to hex str  
    # #####################################################    
    def __u32_unpack(self, u32_byte):    
        temp = struct.unpack('I', u32_byte)[0]
        temp = "%08x"% temp
        if len(temp) == 9:
            temp = temp[0:-1]        
        
        return temp

    # #####################################################
    # function: Convert hex file to bin file.
    # #####################################################
    def Hex_to_Bin(self, hex_file, out_file = None, endian_flag = '0'):   
        #print ('Convert hex file:%s to binary file' %(hex_file))  
        fin = open(hex_file,'r')
        #DataLines = fin.readlines()
        DataLines = fin.read().splitlines()
        fin.close()

        if out_file == None:
            out_file = hex_file[0 : hex_file.rfind('.')] + '.bin'

        fout = open(out_file,'wb')

        str_cut_index = 0
        if DataLines[0].upper().find('0X')>=0:
            str_cut_index = 2
            
        result =''
        
        for eachLine in DataLines:
            #m = re.findall('0x(\w{8})', eachLine)            
            hexString = eachLine[str_cut_index:].strip()
            #print hexString
            if endian_flag == '1': 
                hexString = self.hexStr_obj.AdjustEndian(hexString)
                #print hexString
                #exit(1)
            for i in range(0,len(hexString)/2):
                b = int(hexString[i*2:i*2+2],16)
                result += struct.pack('B',b)               
        fout.write(result)                
        fout.close()
        
    # #####################################################
    # convert bin file to hex file.
    # 
    # #####################################################
    def Bin_to_Hex(self, bin_file, start_addr = 0, length = 'To_End', endian_flag = '0'):
        # adjust inputs: start
        start_addr = (start_addr/4)*4    
        bin_file = open(bin_file, 'rb')   
            
        bin_file.seek(start_addr)
        byte_data = bin_file.read()
        bin_file.close()
        # adjust inputs: length
        if length == 'To_End':
            length = (len(byte_data)/4)*4
        else:
            length = (length/4)*4
            
        OutData = []
        actual_length = length
        index = 0
        while index < length:
            try:
                u32_byte = byte_data[index:(index+4)]
            except:
                print "** Warning: Input length out of range!\n"
                actual_length = index
                break
            try:
                out_str = self.__u32_unpack(u32_byte).upper()
            except:
                print "** Critical: The bin file may not correct! please check!\n"
                exit(-1)
                
            if endian_flag == '1':
                out_str = self.hexStr_obj.AdjustEndian(out_str)            
            OutData.append('0x' + out_str)
            index = index + 4
            
        return (OutData, actual_length)

