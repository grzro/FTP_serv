import socket

HOST = '0.0.0.0'
PORT = 5022  # Port to listen on (non-privileged ports are > 1023)

class ConnHandler:
    def recvUntilRCLF(this):
        data = b''
        while True:
            data += this.conn.recv(1)
            
            if data == b'':
                raise Exception("disconnected")
            
            elif b'\r\n' in data:
                break
            
        return data
        
    def handleCommand(this):
        this.conn.sendall(b"220 Service ready for new user.\r\n") # welcome client
        while not this.sockClosed:
            try:
                this.data = this.recvUntilRCLF()
            except:
                this.closeConn()
            
            command = []
            command = str(this.data, "utf-8").replace('\r\n', ' ').split(' ', 1)
            if len(command) > 1:
                command[1].rstrip()
            print("Client: {}".format(command))
            
            # TODO USER VALIDATION
            if command[0] == 'USER':
                this.conn.sendall(b"331 User name ok, need password.\r\n")
                print("331")
            if command[0] == 'PASS':
                print("230")
                this.conn.sendall(b"230 User logged in.\r\n")
            if command[0] == 'SYST':
                this.conn.sendall(b"215 UNIX Type: L8\r\n")
                print('215')
            if command[0] == 'PWD':
                this.conn.sendall(b"257 workingDir\r\n")
                print('257')
            if command[0] == 'TYPE':
    ############# VELID HERE IF IT IS I-IMAGE OR A-ASCII command[1] ##############################################
                this.conn.sendall(b"200 Command ok.\r\n")
                print('257')
            #if command[0] == 'SIZE':
                #550 File Not Found.
                #213 FileSize
            if command[0] == 'QUIT':
                this.conn.sendall(b"221 Good Bye.\r\n")
                this.closeConn()
    
    def establish(this, port):
        this.sockClosed = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as this.s:
            this.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            this.s.bind((HOST, port))
            this.s.listen(1)
            print("Waiting for connections on port: {}".format(port))
            this.conn, this.addr = this.s.accept()
            with this.conn:
                print('Connected by', this.addr)
                this.s.settimeout(60)
                this.handleCommand()
                    
    def closeConn(this):
        this.s.close()
        this.sockClosed = True
        print('Socket closed')

if __name__ == '__main__':
    srv = ConnHandler()
    srv.establish(PORT)
