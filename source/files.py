import os
from stat import *

class fileSystem:
   def __init__(self):
      self.homePath = os.getcwd()

   def resetPath(self):
      self.chdir(self.homePath)

   def translatePathToServOrder(self, path):
      if '..' in path: # command not allowed
         return None
      if path == '' or path == '/':
         path = self.homePath
      elif 'home' not in path:
         path = self.homePath + '/' + path
      else:
         path = path.replace('home', self.homePath)
      
      path = path.replace('/', '\\')
      path = path.replace('%20', ' ') # Firefox displays it but it actually works
      return path

   def translatePathToNetOrder(self, path):
      home = os.getcwd().replace('/', '\\')
      path = path.replace(self.homePath, 'home')
      path = path.replace('\\', '/')
      path = path.replace(' ', '%20') # Firefox displays it but it actually works
      return path

   def chdir(self, path): # validation of '..' in filepath # SECURITY #######################################################
      try:
         os.chdir(path)
      except:
         print("Can not access: " + path)
         raise Exception
      return path
    
   def getdir(self):
      return os.getcwd()

   def getFileContent(self, filePath, mode): # mode: IMAGE(binary) or ASCII (text)
      if mode == 'I':
         dataMode = 'rb'
      else:
         dataMode = 'rt'

      try:
         f = open(filePath, dataMode)
      except:
         return None

      fileContent = f.read()
      f.close()
      return fileContent

   def getModTime(self, path):
      TS = os.stat(path).st_mtime
      return TS


   def getFileList(self):
      nameList = ''
      files = os.listdir(self.getdir())
      for file in files:
         file = file.replace(' ', '%20') # Firefox displays it but it actually works
         if '.' in file: #it is a file
      # MAKE THE DATA REAL ###########################################################################
            nameList += "-rwxrwx--- 1 root vboxsf 1 Oct 4 21:58 {}\r\n".format(file)
         else: # it is a directory
            nameList += "drwxrwx--- 1 root vboxsf 1 Oct 4 21:58 {}\r\n".format(file)
      return nameList