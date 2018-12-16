import os
from stat import *

class fileSystem:
   def __init__(self):
      self.homePath = os.getcwd()

   def resetPath(self):
      self.chdir(self.homePath)

   def translatePathToServOrder(self, path):
      if '..' in path: # command not allowed, security reasons
         return ''
      if path == '' or path == '/':
         path = self.homePath
      elif 'home' not in path:
         path = self.homePath + '/' + path
      else:
         path = path.replace('home', self.homePath)
      
      path = path.replace('/', '\\')
      return path

   def translatePathToNetOrder(self, path):
      home = os.getcwd().replace('/', '\\')
      path = path.replace(self.homePath, 'home')
      path = path.replace('\\', '/')
      return path

   #func checks if client doesn't want go deeper than home dir
   #temporary implementation
   #useed in CDUP command handler
   def validatePath(self, path):
      if self.homePath in path:
         return True
      else:
         return False

   def chdir(self, path):
      try:
         os.chdir(path)
      except:
         raise Exception
    
   def getdir(self):
      return os.getcwd()

   # mode: IMAGE(binary) or ASCII (text)
   def getFileContent(self, filePath, mode):
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

   # get file modification time
   def getModTime(self, path):
      TS = os.stat(path).st_mtime
      return TS


   def getFileList(self):
      nameList = ''
      files = os.listdir(self.getdir())
      for file in files:
         if '.' in file: #it is a file
      # MAKE THE DATA REAL ###########################################################################
            nameList += "-rwxrwx--- 1 root vboxsf 1 Oct 4 21:58 {}\r\n".format(file)
         else: # it is a directory
            nameList += "drwxrwx--- 1 root vboxsf 1 Oct 4 21:58 {}\r\n".format(file)
      return nameList