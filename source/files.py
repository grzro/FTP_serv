import os

class fileSystem:
   def __init__(self):
      self.homePath = os.getcwd()

   def translatePathToServOrder(self, path):
      path = path.replace('home', self.homePath)
      path = path.replace('/', '\\')
      return path

   def translatePathToNetOrder(self, path):
      home = os.getcwd().replace('/', '\\')
      path = path.replace(self.homePath, 'home')
      path = path.replace('\\', '/')
      return path

   def chdir(self, path): # validation of '..' in filepath # SECURITY #######################################################
      if path == '/':
         path = self.homePath
      try:
         os.chdir(path)
      except:
         print("Can not access: " + path)
         return None
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
      return fileContent

   def getFileList(self):
      nameList = ''
      files = os.listdir(self.getdir())
      for file in files:
         if '.' in file: #it is a file
      # MAKE THE DATA REAL ###########################################################################
            nameList += "-rwxrwx--- 1 root vboxsf 4114 Oct 4 21:58 {}\r\n".format(file)
         else: # it is a directory
            nameList += "drwxrwx--- 1 root vboxsf 4114 Oct 4 21:58 {}\r\n".format(file)
      return nameList