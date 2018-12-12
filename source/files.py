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
        
    def chdir(self, path):
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