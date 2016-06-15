# -*- coding: utf-8 -*-
# ##############################################################################
# class HexStrProcess
#       Function:       class for Hex str process
#       Author:         Fan, Shuangxi (NSN - CN/Hangzhou)
#       draft:          2014-10-14 
#       modify(split):  2015-11-20
#*      description:    
# ##############################################################################
#!/usr/bin/python

    
'''
# ##############################################################################
TODO:

# ##############################################################################
'''
    
# ##############################################################################
# class CHexStrProcess(object):
# [Function]:  class for Hex str process
#
# [Methods]:
# * dec_to_bin: transfor int number to binary string
#    - Input :  dec number
#    - output:  binary string
#   
# * word_split: split a word (4 byte) to some section 
#    - Input :
#          - hex_str:     hex data
#          - bit_len: a list,indicate the bit length of each section
#          - out_len: a list,indicate the format length of the out
#                defult is [], for out data are int numbers
#                if this paramate is not empty,the out data are strings
#          - Order_flag:   indicate the order to get time part
#                0 (default), positive order
#                1,           reverse order         
#   - output: list with int type like ['00','00','00','000']
#
# * SignedIntConvert: unsigned convert to signed int
#
# * AdjustEndian: Invert the Byte order of the hex str.
# ##############################################################################
class CHexStrProcess():
    def __init__(self):
        pass  

    def dec_to_bin(self, int_data):
        bin_data = ''
        tem = bin(int_data)
        if len(tem)<34:
            tem = tem.replace('0b','0b'+'0'*(34-len(tem)))        
        tem = tem.replace('0b','')
        bin_data += tem
        
        return bin_data
    
    # bcakup (^_^)
    def word_split_back(self, hex_str, bit_len, Byte_Endian = 'Little'):
        bin_str = self.dec_to_bin(int(hex_str,16))              
        section_num = len(bit_len)
        out = [[] for i in range(0,section_num)]
        if Byte_Endian.upper() == 'BIG':
            Indx = range(0,section_num)
        elif Byte_Endian.upper() == 'LITTLE':
            Indx = range(0,section_num)[::-1]
            
        section_start = 0
        section_end = 0                  
        for i in Indx:
            section_end += bit_len[i]                    
            out[i] = int(bin_str[section_start:section_end],2)    
            section_start += bit_len[i]       
        return out    

    def word_split(self, hex_str, BitLen, Byte_Endian = 'Little'):
        u32_len = 32
        bit_len = []
        bit_len.extend(BitLen)
        
        section_num = len(bit_len)        
        bit_len_sum = sum(bit_len)
        
        dec = int(hex_str,16)
        
        if section_num == 1 and bit_len[0] == 32:
            return [dec]
        
        # if bit_len_sum < 32, should complete it.
        if bit_len_sum < u32_len:
            bit_len.append(u32_len - bit_len_sum)
        elif bit_len_sum > u32_len:
            print "** Error: bit_len_sum: %d, it must no bigger than 32!\n"% bit_len_sum
            return        
        
        out = [[] for i in range(0,len(bit_len))]        
        if Byte_Endian.upper() == 'BIG':
            for i in range(0,section_num):                    
                out[i] = (dec>>(sum(bit_len[i:])-bit_len[i]))&(2**(bit_len[i])-1)             
        elif Byte_Endian.upper() == 'LITTLE':
            for i in range(0,section_num)[::-1]:                    
                out[i] = (dec>>(sum(bit_len[0:i+1])-bit_len[i]))&(2**(bit_len[i])-1)
                
        return out[0:section_num]


    # unsigned convert to signed int
    def SignedIntConvert(self, int_num, bit_len):
        if int_num>>(bit_len-1):
            out_num = -int_num^(2**bit_len-1)-1
        else:
            out_num = int(int_num)
            
        return out_num

           
    def AdjustEndian(self, hexStr):
        result =  ''
        str_len = len(hexStr)
        #print str_len
        for i in range(0, str_len/2):
            result += hexStr[str_len-(i+1)*2:str_len-i*2]
            #print result
        return result
    
