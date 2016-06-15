# -*- coding: utf-8 -*-
# ##############################################################################
#       Function:       Spalit and parse snapshot buffer
#       Author:         Fan, Shuangxi (NSN - CN/Hangzhou)
#       draft:          2014-10-14 
#       modify(split):  2015-11-20
#*      description:    split snapshot buffer by dump ID, parse each dump block
#           - InputFile:    get snapshot buffer (bin data or hex data)from this file
#           - DstFile:      save parsed info to some files 
# ##############################################################################
#!/usr/bin/python

import os, sys
import logging
import threading
import Tkinter, tkFileDialog

'''
# ##############################################################################
TODO:

# ##############################################################################
'''
 
class CThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func =func
        self.args = args
        
    def run(self):
        apply(self.func, self.args)
        
        
#--------------------------------------------------------------
def debugLogSetup(LogFileName):
    logging.basicConfig(filename = LogFileName,
                        level = logging.WARN, 
                        filemode = 'w', 
                        format =  '%(asctime)s - %(levelname)s: [line:%(lineno)d]: %(message)s',
                        datefmt = '%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)   
    __DEBUG__ = logging.getLogger()
    __DEBUG__.setLevel(logging.DEBUG)
    
    return __DEBUG__
#-------------------------------------------------------------------------
  
        
def getInputFileNamesGui(fileType):
    ftypes = []
    for suf in fileType:
        ftypes.append(tuple(["All files"]) + tuple([suf]))
    master = Tkinter.Tk()
    master.withdraw() # hiding tkinter window
    InputFile = tkFileDialog.askopenfilenames(title="Choose input file", filetypes=ftypes)
    
    return InputFile    


def get_basePathFromArgv(argv):
    if os.path.dirname(argv[0]) != '':      
        basePath = os.path.dirname(argv[0])
    else:
        basePath = os.getcwd() 

    return basePath

  
def get_FileListFromPath(path, fileType):    
              
    fileList = []
    dirDepth = 0
    if os.path.isdir(path):
        dirDepth = 1
        for root,dirs,files in os.walk(path):   
            for fn in files:                
                if fn[fn.rfind('.'):] in fileType:
                    validFile = os.path.join(root, fn)
                    fileList.append(validFile)        
    elif os.path.isfile(path):
        fileList.append(path)
    else:
        print"**Error: '%s' not exit! please check the path and the name of the file.\n"% path
        exit(-1) 
                              
    return (fileList, dirDepth)


def get_FileListFromArgv(argv, fileType):    
    basePath = get_basePathFromArgv(argv)

    if len(argv)==1:
        filepath = getInputFileNamesGui(fileType)
    else:            
        filepath = argv[1]
        
    if os.path.split(filepath)[0] == '':
        filepath = os.path.join(basePath, filepath)

    return get_FileListFromPath(filepath, fileType)


def make_DirByPath(path, suffix_str):
    outDir = path + "_" + suffix_str
    if os.path.isdir(os.path.split(path)[0]) == False:            
        current_path = os.getcwd()
        outDir = os.path.join(current_path, outDir)                
    if os.path.isdir(outDir) == False:
        os.makedirs(outDir)

    return outDir


def make_DirByFilePath(filePath, suffix_str):
    outDir = filePath[0:filePath.rfind('.')] + "_" + suffix_str
    if os.path.isdir(os.path.split(filePath)[0]) == False:            
        current_path = os.getcwd()
        outDir = os.path.join(current_path, outDir)                
    if os.path.isdir(outDir) == False:
        os.makedirs(outDir)

    return outDir


def make_DirByDepth(path, suffix_str, dirDepth):
    
    if 1 == dirDepth:
        path = os.path.split(path)[0]

    if os.path.isdir(path) == False:
        return  make_DirByFilePath(path, suffix_str)
    else:
        return make_DirByPath(path, suffix_str)
  

# map: keys-> values
# creat a dictionary
def creat_dictionary(keys, values):
    Out_Dic = dict.fromkeys(keys, None)
    
    dic_size = min(len(keys), len(values))
    for i in range(0, dic_size):
        Out_Dic[keys[i]] = values[i]

    return Out_Dic

