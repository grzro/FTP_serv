import os
import shutil
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

   def mkdir(self, dirName):
      try:
         os.mkdir(dirName)
      except:
         raise Exception

   #remove dir even if it contains something
   def remdir(self, dirName):
      dirPath = self.getdir() + '\\' + dirName
      try:
         shutil.rmtree(dirPath)
      except:
         raise Exception
   
   def deleteFile(self, fName):
      try:
         os.remove(fName)
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

   # if there is a file with the same name,
   # content will be replaced
   def storeFile(self, fName, fData):
      try:
         file = open(fName, 'wb')
         file.write(fData)
      except:
         raise Exception

   # get file modification time
   def getModTime(self, path):
      TS = os.stat(path).st_mtime
      return TS

   def getFileSize(self, fName):
      fPath = self.getdir() + '\\' + fName
      FS = os.stat(fPath).st_size
      return FS

   def getFileList(self):
      nameList = ''
      files = os.listdir(self.getdir())
      for file in files:
         if '.' in file: #it is a file
            nameList += "-rwxrwx--- 1 root vboxsf {} Oct 4 21:58 {}\r\n".format(self.getFileSize(file), file)
         else: # it is a directory
            nameList += "drwxrwx--- 1 root vboxsf Oct 4 21:58 {}\r\n".format(file)
      return nameList