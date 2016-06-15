#======================================================================================
#       Function:       classes for pcap file decode, and protocol, message decode
#       Author:         Fan Shaungxi(Fan, Shuangxi (NSN - CN/Hangzhou))
#       Date:           2014-09-14
#*  *   description:    This script include the classes can decoding of:
#                       pcap header, pcap packet, Ethernet, Ip, udp, data part (message)
#======================================================================================

#!/usr/bin/python

#coding=utf-8

import struct
from GlobDef import *


# ###############################################################
# base class: include transition functions and 1 disply function:
#           Byte_to_hex:
#           str_to_hex: transform stream to hex,
#                       like '\x01\x0e\0xb0' to '0x010eb0'
#           str_to_bin:
#           str_to_dec:
#           hexdata_disp:
# ###############################################################
class Base(object):
    def __init__(self):
        pass
    # #####################################################
    def Byte_to_hex(self, Byte_data):
        hex_data = []
        for i in range(0,len(Byte_data)):
            temp = ''
            temp = ord(Byte_data[i])
            temp = hex(temp)
            if len(temp)==3:
                temp = temp.replace('0x','0x0')
            temp = temp.replace('0x',' ')
            hex_data.append(temp)            
        return hex_data
    
    # #####################################################
    def str_to_hex(self, strs):
        hex_data = ''
        for i in range(len(strs)):
            tem = ord(strs[i])
            tem = hex(tem)
            if len(tem)==3:
                tem = tem.replace('0x','0x0')
            tem = tem.replace('0x','')
            hex_data += tem
        return '0x'+hex_data
    
    # #####################################################
    def str_to_bin(self,strs):
        bin_data = ''
        for i in range(len(strs)):
            tem = ord(strs[i])
            tem = bin(tem)
            if len(tem)<10:
                tem = tem.replace('0b','0b'+'0'*(10-len(tem)))                
            tem = tem.replace('0b','')
            bin_data += tem            
        return '0b'+ bin_data
    
    # #####################################################        
    def str_to_dec(self,strs):
        dec_data = 0
        for i in range(len(strs)):
            tem = ord(strs[i])
            dec_data += tem*(256**(len(strs)-i-1))            
        return dec_data
    
    # #####################################################
    #*  description: endian transform for hex data
    #   - Input :  hex data list
    #   - output:  hex data after endian transform
    # #####################################################
    def endian_transform(self, data):    
        data_num = len(data)
        #print " - endian transform ...\n"
        #print "   - data number: %d\n" % data_num
        post_data = []
        header = ''
        start = 0
        if data[0].find('0x')>=0:
            header = '0x'
            start = 2            
        for i in range(0,data_num):
            data_i = data[i][start:]
            tran_data_i = ''
            byte_len = len(data_i)/2
            for j in range(0,byte_len):
                tran_data_i += data_i[(byte_len-1-j)*2:(byte_len-j)*2]
            post_data.append(header+tran_data_i)
            
        return post_data

    # #####################################################
    def hexdata_disp(self, hex_data):
        raw_data = []
        asc_data = []
        disp_data = []
        for i in range(len(hex_data)):
            raw_data.append(hex_data[i])
            asc = int(hex_data[i],16)
            if(asc>=32 and asc<=126):
                asc_data.append(chr(asc))
            else:
                asc_data.append('.')
        while(len(raw_data)%16!=0):
            raw_data.append('   ')
            asc_data.append(' ')
        temp1 = ''
        temp2 = ''
        rownum = 0
        for j in range(len(raw_data)):
            if (j==0 or j%16!=0):
                temp1 = temp1+raw_data[j]
                temp2 = temp2+asc_data[j]
            elif j%16==0:
                temp1 = '0'*(4-len('%d'%(rownum*10)))+ ('%d'%(rownum*10)) + temp1+' ; '+temp2
                rownum += 1
                disp_data.append(temp1)
                temp1 = ''
                temp2 = ''
                temp1=temp1+raw_data[j]
                temp2=temp2+asc_data[j]
        temp1 = '0'*(4-len('%d'%(rownum*10)))+ ('%d'%(rownum*10)) + temp1+' ; '+temp2
        disp_data.append(temp1)        
        return disp_data

# ########################################################
# pcap file decode :
#       header_decode:          decode pcap header
#       pcaket_decode:          decode packet
#       get_pcap_header_str:    orgnaize the decoded data of pcap header
#       get_packet_header_strs: orgnaize the decoded data of packet headers
# ########################################################
class Pcap(Base):
    def __init__(self, pcap_fileName = None):
        self.pcap_fileName = pcap_fileName
        self.fpcap = open(self.pcap_fileName,'rb')
        self.stream_data = self.fpcap.read()
        self.pcap_header_items = ['magic_number',
                                  'version_major',
                                  'version_minor',
                                  'thiszone',
                                  'sigfigs',
                                  'snaplen',
                                  'linktype']
        self.pcap_header_values = [0 for i in range(0,7)]
        self.packet_header_items = ['GMTtime',
                                    'MicroTime',
                                    'caplen',
                                    'len']        
        self.packet_header_values = [[] for i in range(0,4)]    
        self.packet_num = 0
        self.endian_flag = 0  # 0 no need change, 1 need change
        self.caplen_len = []
        self.packet_data = []
        self.pcap_headerstr =''
        self.packet_headerstrs =[]                                   

    def pcap_decode(self):        
        self.header_decode()
        self.pcaket_decode()        
        self.get_pcap_header_str()
        self.get_packet_header_strs()
        
        self.fpcap.close()
        
    def header_decode(self):
        
        """     |------------Pcap File Header----------|
                        
            4 bytes       2 bytes     2 bytes     4 bytes    4 bytes   4 bytes   4 bytes
            ------------------------------------------------------------------------------
    Header  | magic_num | ver_major | ver_minor | timezone | sigfigs | snaplen | linktype|
            ------------------------------------------------------------------------------
        """ 
        
        self.pcap_header_values[0] = self.stream_data[0:4]
        self.pcap_header_values[1] = self.stream_data[4:6]
        self.pcap_header_values[2] = self.stream_data[6:8]
        self.pcap_header_values[3] = self.stream_data[8:12]
        self.pcap_header_values[4] = self.stream_data[12:16]
        self.pcap_header_values[5] = self.stream_data[16:20]
        self.pcap_header_values[6] = self.stream_data[20:24]        

    def pcaket_decode(self): 
        
        """     |------------Packet Header----------|

                 4 bytes   4 bytes    4 bytes 4 bytes   
            ----------------------------------------------
        Packet  | GMTtime | MicroTime | CapLen | Len |  Data |
            ----------------------------------------------
        """  
        global pcap_header_len
        i = pcap_header_len  # 24
        while(i<len(self.stream_data)):
            # packet header
            self.packet_header_values[0].append(self.stream_data[i:i+4])
            self.packet_header_values[1].append(self.stream_data[i+4:i+8])
            self.packet_header_values[2].append(self.stream_data[i+8:i+12])
            self.packet_header_values[3].append(self.stream_data[i+12:i+16])

            if self.pcap_header_values[0][0].find('d4')>0:
                self.endian_flag = 1
                               
            this_packet_len = struct.unpack('I',self.packet_header_values[2][self.packet_num])[0]                        
            self.caplen_len.append(this_packet_len)
            # write the data
            self.packet_data.append(self.stream_data[i+16:i+16+this_packet_len])
            i += (this_packet_len + 16)
            self.packet_num += 1            

    def get_pcap_header_str(self):        
        self.pcap_headerstr += "**********************************\n"
        self.pcap_headerstr += "Pcap file header info:\n"        
        for i in range(0, len(self.pcap_header_items)):
            self.pcap_headerstr += (self.pcap_header_items[i] + " : ")
            hex_data = self.Byte_to_hex(self.pcap_header_values[i])
            for j in range(0,len(hex_data)):
                self.pcap_headerstr += hex_data[j]
            self.pcap_headerstr += '\n'          
        self.pcap_headerstr += "Total packet number: ( %d )\n"% self.packet_num
        self.pcap_headerstr += "**********************************\n"
        
    def get_packet_header_strs(self):     
        for i in range(0, self.packet_num):
            packet_headerstr = ("packet number: [%d]\n" % i)
            for k in range(0,len(self.packet_header_items)):
                hex_data = self.Byte_to_hex(self.packet_header_values[k][i])
                datastr = ''
                for j in range(0,len(hex_data)):
                    datastr += hex_data[j]
                packet_headerstr += " %s: %s\n"%(self.packet_header_items[k],datastr)
            packet_headerstr += " Frame (%d bytes):\n" % self.caplen_len[i]            
            self.packet_headerstrs.append(packet_headerstr)    

# ########################################################
# Ethernet Protocol decode:
#       decode Ethernet header
# ########################################################
class Ethernet(Base):
    
    def __init__(self, datastr = None, data_start = 0):        
        self.src = None
        self.dst = None
        self.ethertype = None
        self.len = None
        self.type = None
        self.printstr = ''
        self.datastr = datastr[data_start:]
        
    def frame_decode(self):        
        tem = self.str_to_hex(self.datastr[0:6])        
        self.dst = tem[2:4]+':'+tem[4:6]+':'+tem[6:8]+':'\
                   +tem[8:10]+':'+tem[10:12]+':'+tem[12:14]
        tem = self.str_to_hex(self.datastr[6:12])
        self.src = tem[2:4]+':'+tem[4:6]+':'+tem[6:8]+':'\
                   +tem[8:10]+':'+tem[10:12]+':'+tem[12:14]
        srcstr = 'Src: '+self.src
        dststr = 'Dst: '+self.dst
        
        unknow = self.str_to_hex(self.datastr[12:14])
        tem = int(unknow,16)        
        if tem<=1500:
            self.ethertype='IEEE 802.3 Ethernet'
            self.len =tem
            lenstr = 'Length: '+str(self.len)
            return [self.ethertype, dststr,srcstr,lenstr]

        elif tem>=1536:
            self.ethertype='Eternet II'
            global EtherType
            self.type = EtherType[unknow]
            typestr = 'Type: '+self.type+'('+ unknow+')'
            
        self.printstr = '\n%s, %s, %s\n  %s\n'\
                   %(self.ethertype,srcstr,dststr,typestr)
        

# ########################################################
# 802.1Q Vlan Protocol decode:
#       Vlan decode 
# ########################################################
class Vlan(Base):
    
    global Ethernet_header_len
    
    def __init__(self, datastr = None, data_start = Ethernet_header_len):
        self.PRI =None
        self.CFI =None
        self.ID =None
        self.type = None
        self.printstr = ''
        self.datastr = datastr[data_start:]
        
        global Vlan_header_len
        self.header_len = Vlan_header_len
        
    def frame_decode(self):        
        tem = self.str_to_bin(self.datastr[0])[2:]+self.str_to_bin(self.datastr[1])[2:]        
        self.PRI = str(int(tem[0:3],2))
        self.CFI = str(int(tem[3],2))
        self.ID = str(int(tem[4:16],2))
        
        type_ID = self.str_to_hex(self.datastr[2:4])
        self.type = EtherType[type_ID]
            
        self.printstr = '\n802.1Q Virtual LAN, PRI: %s, CFI: %s, ID: %s\n  Type: %s (%s)\n'\
                   %(self.PRI,self.CFI,self.ID,self.type,type_ID)          
# ########################################################
# Internet Protocol decode
#       decode Internet Protocol header
# ########################################################
class Internet(Base):
    '''
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |Version| IHL |Type of Service| Total Length |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | Identification |Flags| Fragment Offset |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | Time to Live | Protocol | Header Checksum |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | Source Address |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | Destination Address |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | Options | Padding |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    '''
    
    def __init__(self,datastr = None, data_start = Ethernet_header_len):
        self.version = None
        self.Hd_len = None
        self.service_type = None
        self.total_len = None
        self.id = None
        self.flags = None
        self.flags_str = None
        self.flag_str = [None,None,None]
        self.offset = None
        self.ttl = None
        self.protocol = None
        self.protocol_num = None
        self.Hd_checksum = None
        self.src = None                
        self.dst = None
        self.printstr = ''
        self.datastr = datastr[data_start:]

    def frame_decode(self):
        
        tem = self.str_to_bin(self.datastr[0])
        self.version = int(tem[2:6],2)
        self.Hd_len = int(tem[6:10],2)*4
        self.service_type = self.str_to_hex(self.datastr[1])
        self.total_len = self.str_to_dec(self.datastr[2:4])
        self.id = self.str_to_hex(self.datastr[4:6])
        tem = self.str_to_bin(self.datastr[6:8])
        self.flags = tem[0:5]
        if self.flags[3] == '1':
            self.flags_str = "(Don't fragment)"
        else:
            self.flags_str = "(More fragments)"
            
        self.flag_str[0] = "%s... .... = Reserved bit: "%(self.flags[2]) 
        self.flag_str[1] = ".%s.. .... = Don't fragment"%(self.flags[3])
        self.flag_str[2] = "..%s. .... = More fragments"%(self.flags[4])
        for i in range(0,3):                
            if self.flags[2+i] == '0':
                self.flag_str[i] += "Not set"
            else:
                self.flag_str[i] += "Set"
        
        self.offset = int(tem[5:],2)
        self.ttl = self.str_to_dec(self.datastr[8])
        global ProtocolType
        self.protocol = ProtocolType[self.str_to_hex(self.datastr[9])]
        self.protocol_num = self.str_to_dec(self.datastr[9])        
        self.Hd_checksum = self.str_to_hex(self.datastr[10:12])        
        tem = self.str_to_hex(self.datastr[12:16])
        self.src = str(int(tem[2:4],16))+'.'+str(int(tem[4:6],16))+\
                   '.'+str(int(tem[6:8],16))+'.'+str(int(tem[8:10],16))
        tem = self.str_to_hex(self.datastr[16:20])
        self.dst = str(int(tem[2:4],16))+'.'+str(int(tem[4:6],16))+\
                   '.'+str(int(tem[6:8],16))+'.'+str(int(tem[8:10],16))

        self.get_print_str()
        
    def get_print_str(self):
        self.printstr += 'Internet Protocol version %d, Src: %s, Dst: %s\n'\
                         %(self.version, self.src, self.dst)
        self.printstr += '  Header Length: %d bytes\n  Service: %s\n'\
                         %(self.Hd_len, self.service_type)
        self.printstr += '  Total Length: %d\n  Identification: %s (%d)\n'\
                         %(self.total_len, self.id, int(self.id,16))
        self.printstr += '  Flags: %s %s\n   %s\n   %s\n   %s\n'\
                         %(self.flags, self.flags_str, self.flag_str[0], self.flag_str[1], self.flag_str[2])
        self.printstr += '  Fragment offset: %d\n'\
                         %(self.offset)
        self.printstr += '  Time to live: %d\n'\
                         %(self.ttl)
        self.printstr += '  Protocol: %s (%d)'\
                         %(self.protocol, self.protocol_num)
        self.printstr += '  Header checksum: %s\n'\
                         %(self.Hd_checksum)
        self.printstr += '  Source: %s\n  Destination: %s\n'\
                         %(self.src, self.dst)            


# ########################################################
# User Datagram Protocol decode
#       decode udp header
#       get data part of the udp packet
# ########################################################
class Udp(Base):
    
    global Ip_header_len
    
    def __init__(self, datastr = None, data_start = Ethernet_header_len + Ip_header_len):
        
        self.src_port = None
        self.dst_port = None
        self.len = None
        self.checksum = None
        self.data = None
        self.printstr = ''        
        self.datastr = datastr[data_start:]
                
    def frame_decode(self):
        self.src_port = self.str_to_dec(self.datastr[0:2])
        self.dst_port = self.str_to_dec(self.datastr[2:4])
        self.len = self.str_to_dec(self.datastr[4:6])
        self.checksum = self.str_to_hex(self.datastr[6:8])

        self.get_print_str()

    def get_print_str(self):
        self.printstr += 'User Datagram Protocol, Src Port: %d, Dst Port: %d\n'\
                         %(self.src_port, self.dst_port)
        self.printstr += '  Source Port: %d\n  Destination Port: %d\n'\
                         %(self.src_port, self.dst_port)
        self.printstr += '  Length: %d\n'\
                         %(self.len)
        self.printstr += '  Checksum: %s\n'\
                         %(self.checksum)
        
        # ------ data part ----------
        global Udp_header_len
        self.printstr += 'Data(%d bytes): \n'\
                         %(self.len - Udp_header_len)
        self.data = self.Byte_to_hex(self.datastr[Udp_header_len:self.len])
        disp_data = self.hexdata_disp(self.data)
        for j in range(0, len(disp_data)):
            self.printstr += (disp_data[j] + '\n')        
        
        
# ########################################################            
# Message data decode
#       decode the data part of the udp
#       messages decode, accronding to the message struct
# ########################################################
class Message(Base):
    
    def __init__(self, datastr = None):
        self.print_level_1 = 1
        
        self.msgId = None
        self.msgName = None
        self.items = []
        self.msg_value = []
        self.hex_value = []
        self.dec_value = []
        self.seekptr = 0
        global msg_header_len
        self.msg_header_len = 10 # for the endian model transform control
        self.printstr = ''
        self.byte_offset = 0

        hex_datastr = ''.join(datastr)
        hex_datastr = hex_datastr.replace(' ','')
        self.datastr = hex_datastr
        
        global MessageId
        for key in MessageId:
            tem = self.datastr[0:4*2].find(key)
            if tem > 0:
                break
            
        self.msgId = key
        self.msgName = MessageId[key][1]
        msg_struct = MessageId[key][0]
        
        # get dynamic_num_indx
        if msg_struct[0][0]>0:
            self.dynamic_num_indx = msg_struct[0][0]-1
        else:
            self.dynamic_num_indx = msg_struct[0][0]
                        
        self.dynamic_num = None
        self.dynamic_single_len = msg_struct[0][1]        
        self.msg_struct = msg_struct[1] + msg_struct[2]
        
        for k in range(0,len(self.msg_struct)):
            self.items.append(self.msg_struct[k][0])        
            
    def frame_decode(self):

        # the endian model of the first 10 items(16 bytes) has been transformed
        # so, here no need to transform the endian model        
        self.add_values(0, self.msg_header_len)
            
        if self.dynamic_num_indx == 0:                         
            # from the 10th item, the endian model should be transform        
            self.add_values(self.msg_header_len, len(self.msg_struct))
            
        # for dynamic situation
        elif self.dynamic_num_indx > 0: 
            self.add_values(self.msg_header_len, self.dynamic_num_indx+1)
            for i in range(0, self.dynamic_num):
                self.add_values(self.dynamic_num_indx+1, self.dynamic_num_indx+1 + self.dynamic_single_len)
                
        self.get_print_str()  
        if  self.dynamic_num > 0:
            for i in range(1, self.dynamic_num):
                self.msg_struct += self.msg_struct[self.dynamic_num_indx+1: self.dynamic_num_indx+1+ self.dynamic_single_len]
                for j in range(self.dynamic_num_indx+1, self.dynamic_num_indx+1+self.dynamic_single_len):
                    self.items.append(self.msg_struct[j][0]) 

    def add_values(self, start, end):        
        for i in range(start, end):
            field_len = self.msg_struct[i][1]
            value = self.datastr[self.seekptr : self.seekptr + field_len*2]
            if field_len>2 and start >= self.msg_header_len:   # change endian model      
                value = ''       
                for j in range(0,field_len):            
                    value += self.datastr[self.seekptr + (field_len-j-1)*2 : self.seekptr + (field_len-j)*2]
   
            self.hex_value.append(value)
            #print "***value:*%s*"% value
            self.dec_value.append(int(value,16))
            hex_data = hex(int(value,16))[2:]
            if len(hex_data)>8:  # in considition of the type like '0x95030000L'
                hex_data = hex_data[0:8]
            self.msg_value.append(hex_data)
            self.seekptr += field_len*2
            
            # find dynamic number, if finded, stop add value
            if self.dynamic_num_indx>0 and self.dynamic_num_indx == i:
                self.dynamic_num = int(value,16)

                break
        
    def get_print_str(self):        
        self.printstr +='\n%s: 0x%s\n'%(self.msgName, self.msgId)
        self.printstr +='Byte offset Node name(length) value hex  GUI value\n'

        # for fix part
        self.get_print_values(0, 0, len(self.msg_struct))
        
        # for dynamic situation, add dynamic part       
        if self.dynamic_num_indx >1:
            for i in range(0, self.dynamic_num-1):                
                self.get_print_values(self.dynamic_num_indx+1, (i+1)*self.dynamic_single_len, self.dynamic_single_len)


    def get_print_values(self, field_start, data_offset, data_len):

        for k in range(field_start, field_start + data_len):
            interval_1 = ' '*(20 - len(self.msg_struct[k][0]))
            interval_2 = ' '*(10 - len(self.hex_value[k]))
            print_values = (self.byte_offset,\
                            self.msg_struct[k][0],\
                            self.msg_struct[k][1],\
                            interval_1,\
                            self.hex_value[data_offset + k],\
                            interval_2,\
                            self.msg_value[data_offset + k])                   
            self.printstr +='  %2d  %s(%d)%s  %s  %s  %s\n'% print_values
            self.byte_offset += self.msg_struct[k][1]
            
# ########################################################              
