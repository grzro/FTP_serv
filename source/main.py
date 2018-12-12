import files
import socket
import os
from test.test_decimal import file

HOST = '0.0.0.0'
PORT = 5022  # Port to listen on (non-privileged ports are > 1023)

class ConnHandler:
    def recvUntilRCLF(self):
        data = b''
        while True:
            data += self.conn.recv(1)
            
            if data == b'':
                raise Exception("disconnected")
            
            elif b'\r\n' in data:
                break
            
        return data
    
    def handlePASV(self):
        ip = (127, 0, 0, 1) #### TODO #####################################################################
        p = self.dataPort
        reply = b"227 Entering Passive Mode (%i,%i,%i,%i,%i,%i).\r\n" % (
            ip[0], ip[1], ip[2], ip[3], 
            p / 256, p % 256
        )
        self.conn.sendall(reply)
        print('227')
        
    def handleLIST(self, dir):
        self.conn.sendall(b"150 Data connection already open; IMAGE transfer starting.\r\n")
        print('125')
        self.connData, self.addrData = self.sData.accept()
        
        ################################################## MOVE IT TO FILES.PY ####################################
        nameList = ""
        if dir in ('-l', ''):
            files = os.listdir(os.getcwd())
            for file in files:
                if '.' in file: #it is a file
                    # MAKE THE DATA REAL ###########################################################################
                    nameList += "-rwxrwx--- 1 root vboxsf 4114 Oct  4 21:58 {}".format(file)
                    nameList += '\r\n'
                else: # it is a directory
                    nameList += "drwxrwx--- 1 root vboxsf 4114 Oct  4 21:58 {}".format(file)
                    nameList += '\r\n'
                    
        ############################################################################################################

        self.connData.sendall(bytes(nameList, "utf-8"))
        self.connData.shutdown(socket.SHUT_RDWR)
        self.connData.close()
        self.conn.sendall(b'226 Transfer complete\r\n')
        print('226')
        
    def handleRETR(self, file):
        if '.'not  in file: # it is not a file
            self.conn.sendall(b"550 Requested action not taken.\r\n")
            print('550 invalid path')
            return
        
        self.conn.sendall(b"150 Data connection already open; IMAGE transfer starting.\r\n")
        print('125')
        self.connData, self.addrData = self.sData.accept()
        
        filepath = self.fileSystem.translatePathToServOrder(file)
        fileContent = self.fileSystem.getFileContent(filepath, self.dataType)
        
        if not fileContent:
            self.connData.sendall(b"451 Requested action aborted. Local error in processing.\r\n")
            return
        
        self.connData.sendall(fileContent)
        self.connData.shutdown(socket.SHUT_RDWR)
        self.connData.close()
        self.conn.sendall(b'226 Transfer complete\r\n')
        print('226')
        
    def handleCommand(self):
        
        self.conn.sendall(b"220 Service ready for new user.\r\n") # welcome client
        
        while not self.sockClosed:
            try:
                self.data = self.recvUntilRCLF()
            except:
                self.closeConn()
            
            command = []
            command = str(self.data, "utf-8").replace('\r\n', ' ').split(' ', 1)
            command[1] = command[1].replace(' ', '')
            
            print("Client: {}".format(command))
            
            # TODO USER VALIDATION ###############################################################################
            if command[0] == 'USER':
                self.conn.sendall(b"331 User name ok, need password.\r\n")
                print("331")
            if command[0] == 'PASS':
                print("230")
                self.conn.sendall(b"230 User logged in.\r\n")
            if command[0] == 'SYST':
                self.conn.sendall(b"215 UNIX Type: L8\r\n")
                print('215')
            if command[0] == 'PWD':
                reply = "257 " + self.fileSystem.translatePathToNetOrder(self.fileSystem.getdir()) + "\r\n"
                self.conn.sendall(bytes(reply, "utf-8"))
                print('257')
            if command[0] == 'TYPE':
                self.conn.sendall(b"200 Command ok.\r\n")
                self.dataType = command[1] # IF IT IS IMAGE OR ASCII
                print('257')
            if command[0] == 'SIZE':
                self.conn.sendall(b"213 123\r\n") # 123 -> SIZE - ONLY FOR TESTING ###############################
                print('213')
            if command[0] == 'CWD':
                # validation of '..' in filepath # SECURITY #######################################################
                if self.fileSystem.chdir(self.fileSystem.translatePathToServOrder(command[1])):
                    self.conn.sendall(b"250 Requested file action completed.\r\n")
                    print('250')
                else:
                    self.conn.sendall(b"550 File not found.\r\n")
                    print('550 Invalid path while CWD')
            if command[0] == 'PASV':
                self.handlePASV()
            if command[0] == 'LIST':
                self.handleLIST(command[1])
            if command[0] == 'RETR':
                self.handleRETR(command[1])
            if command[0] == 'QUIT':
                self.conn.sendall(b"221 Good Bye.\r\n")
                self.closeConn()
    
    def establish(self, port):
        self.fileSystem = files.fileSystem()
                
        self.sData = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sData.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sData.bind((HOST, 0))
        self.dataPort = self.sData.getsockname()[1]
            
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((HOST, port))
        
        while True:
            self.sData.listen(1)
            self.s.listen(1)
            print("Waiting for connections on port: {}".format(port))
            self.conn, self.addr = self.s.accept()
            self.sockClosed = False
            with self.conn:
                print('Connected by', self.addr)
                self.s.settimeout(60)
                self.handleCommand()
        self.s.close()
                    
    def closeConn(self):
        self.conn.close()
        self.sockClosed = True
        print('Socket closed')

if __name__ == '__main__':
    srv = ConnHandler()
    srv.establish(PORT)
