import files
import connection_manager
import os

class ConnHandler:

	def handleUSER(self, arg):
		self.client.sendMsgData(b"331 User name ok, need password.\r\n")

	def handlePASS(self, arg):
		self.client.sendMsgData(b"230 User logged in.\r\n")

	def handleSYST(self, arg):
		self.client.sendMsgData(b"215 UNIX Type: L8\r\n")

	def handleFEAT(self, arg):
		self.client.sendMsgData(b"211 \r\n") #Server has no features at all

	def handleMDTM(self, arg): # Last file modification time
		path = self.fileSystem.translatePathToServOrder(arg)
		time = self.fileSystem.getModTime(path)
		reply = "213 {}\r\n".format(time)
		self.client.sendMsgData(bytes(reply, "utf-8"))

	def handlePWD(self, arg):
		'''
		Actually it has no matter if it is real working directory.
		'home' allow to work both on Google Chrome and Mozilla Firefox
		'''
		path = 'home'
		reply = "257 " + path + "\r\n"
		self.client.sendMsgData(bytes(reply, "utf-8"))

	def handleTYPE(self, arg):
		self.client.sendMsgData(b"200 Command ok.\r\n")
		self.dataType = arg # IF IT IS IMAGE OR ASCII

	def handleSIZE(self, arg):
		self.client.sendMsgData(b"213 123\r\n") # size has no matter in fact

	def handleCWD(self, arg):
		path = self.fileSystem.translatePathToServOrder(arg)
		try:
			self.fileSystem.chdir(path) # .translatePath returns None if arg contains '..'
		except:
			self.client.sendMsgData(b"550 File not found.\r\n")
			print('Invalid path')
			return

		self.client.sendMsgData(b"250 Requested file action completed.\r\n")

	def handlePASV(self, arg):
		ip, p = self.client.getDTConnInfo()
		ip = ip.split('.') #spliting IP for numbers
		reply = b"227 Entering Passive Mode (%i,%i,%i,%i,%i,%i).\r\n" % (
			int(ip[0]), int(ip[1]), int(ip[2]), int(ip[3]),
			p / 256, p % 256
		)
		self.client.sendMsgData(reply)
 
	def handleLIST(self, dir):
		self.client.sendMsgData(b"150 Data connection already open; IMAGE transfer starting.\r\n")
		self.client.acceptDTConn()
		
		if dir in ('-l', ''):
			nameList = self.fileSystem.getFileList()

		self.client.sendDTData(bytes(nameList, "utf-8"))
		self.client.closeDTConn()
		self.client.sendMsgData(b'226 Transfer complete\r\n')
		print('Directories listed')

	def handleRETR(self, file):
		if '.'not in file: # it is not a file
			self.client.sendMsgData(b"550 Requested action not taken.\r\n")
			print('invalid path')
			return

		self.client.sendMsgData(b"150 Data connection already open; IMAGE transfer starting.\r\n")
		self.client.acceptDTConn()
	 
		filepath = self.fileSystem.translatePathToServOrder(file)
		fileContent = self.fileSystem.getFileContent(filepath, self.dataType)
		 
		if not fileContent:
			self.client.sendDTData(b"451 Requested action aborted. Local error in processing.\r\n")
			return
		 
		self.client.sendDTData(fileContent)
		self.client.closeDTConn()
		self.client.sendMsgData(b'226 Transfer complete\r\n')
		print('File sent')

	def handleQUIT(self, arg):
		self.client.sendMsgData(b"221 Good Bye.\r\n")
	 
	def commandManagement(self):
		#self.fileSystem.resetPath()
		self.client.sendMsgData(b"220 FTP Server by GrzRo. Hello.\r\n") # welcome client
		 
		while self.client.isMsgConnOpen():
			try:
				self.data = self.client.recvMsg()
			except:
				print('no more data from client')
				return
		 
			cmd, arg = str(self.data, "utf-8").replace('\r\n', ' ').split(' ', 1)
			arg = arg.replace(' ', '')

			print("Client: {} {}".format(cmd, arg))

			if cmd in self.methods:
				self.methods[cmd](arg)
			else:
				print("Unknown method: " + cmd + arg)

	def establish(self, port):
		self.fileSystem = files.fileSystem()
		self.client = connection_manager.ConnectionManager()

		# automatically add all methods which starts with 'handle'
		# to avoid writing if cmd == 'xxxx': handleCMD() many times
		self.methods = {}
		for method_name in dir(self):
			if method_name.startswith("handle"):
				cmd = method_name.replace("handle", "")
				self.methods[cmd] = getattr(self, method_name)

		self.client.bindMsgConn(HOST, PORT)
		self.client.bindDTConn(0) #random port, host the same as in MSG-Conn

		while True:
			self.client.listenMsgConn()
			self.client.listenDTConn()
			print("Waiting for connections on port: {}".format(port))
			self.client.acceptMsgConn()
			print("Client connected")
			self.commandManagement()
		
if __name__ == '__main__':
	HOST = '0.0.0.0'
	PORT = 5022

	srv = ConnHandler()
	srv.establish(PORT)
