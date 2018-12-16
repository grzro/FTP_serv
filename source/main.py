import files
import connection_manager
import os

class ConnHandler:

	def handleCDUP(self, arg):
		currPath = self.fileSystem.getdir()
		dirs = currPath.split('\\')
		del dirs[len(dirs) - 1] # remove last dir name
		newPath = '\\'.join(dirs)
		print(newPath)
		if self.fileSystem.validatePath(newPath):
			self.fileSystem.chdir(newPath) # <-- raises exception
			self.client.sendMsgData(b"250 Requested file action completed.\r\n")
		else:
			self.client.sendMsgData(b"550 File not found.\r\n")
			print('Server: Invalid path: ' + newPath)

	def handleUSER(self, arg):
		self.client.sendMsgData(b"331 User name ok, need password.\r\n")

	def handlePASS(self, arg):
		self.client.sendMsgData(b"230 User logged in.\r\n")

	def handleSYST(self, arg):
		self.client.sendMsgData(b"215 UNIX Type: L8\r\n")

	def handleFEAT(self, arg):
		self.client.sendMsgData(b"211 \r\n") #Server has no features

	def handleMDTM(self, arg): # Last file modification time
		path = self.fileSystem.translatePathToServOrder(arg)
		time = self.fileSystem.getModTime(path)
		reply = "213 {}\r\n".format(time)
		self.client.sendMsgData(bytes(reply, "utf-8"))

	# RFC 2228
	def handleAUTH(self, arg):		#no TLS nor SSL
		self.client.sendMsgData(b"500 No authorisation.\r\n")

	def handleHELP(self, arg):          #HELP SITE
		self.client.sendMsgData(b"202 Im not so helpful.\r\n")

		#client opens port to transferr data
	def handlePORT(self, arg): #We prefer to control Data Transfer #security
		self.client.sendMsgData(b"421 Only PASV.\r\n") #switch to PASV

	def handlePWD(self, arg):
		'''
		Actually it has no matter if it is real working directory.
		'home' allow to work both on Google Chrome (demand it) and 
		Mozilla Firefox (no matter what we send here)
		UPDATE:
		FF works with everything
		TotalCommander with current path
		FileZilla must start from '/'
		Chrome need to have costant path here f.eg. 'home', no matter on which dir it is operating
		'''

		#path = '/'
		path = self.fileSystem.getdir()
		translatedPath = self.fileSystem.translatePathToNetOrder(path)
		reply = "257 " + translatedPath + "\r\n"
		self.client.sendMsgData(bytes(reply, "utf-8"))

	def handleCWD(self, arg):
		try:
			self.fileSystem.chdir(arg) # try relative path
		except:
			try:
				# try absolute path
				path = self.fileSystem.translatePathToServOrder(arg)
				self.fileSystem.chdir(path)
			except:
				self.client.sendMsgData(b"550 File not found.\r\n")
				print('Server: Invalid path: ' + path)
				return

		self.client.sendMsgData(b"250 Requested file action completed.\r\n")

	def handleOPTS(self, arg):
		arg = arg.upper()
		if arg == 'UTF8 ON':
			reply = b"200 utf-8 ON.\r\n" # reply, YES
		else:
			reply = b"451 NO OPT\r\n" # No other options
		
		self.client.sendMsgData(reply)

	def handleTYPE(self, arg):
		self.client.sendMsgData(b"200 Command ok.\r\n")
		self.dataType = arg # IF IT IS IMAGE OR ASCII

	def handleSIZE(self, arg):
		self.client.sendMsgData(b"550 123\r\n") #213 if ok size has no matter in fact

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
		print('Server: Directories listed')

	def handleRETR(self, file):
		if '.' not in file: # it is not a file
			self.client.sendMsgData(b"550 Requested action not taken.\r\n")
			print('Server: invalid path')
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
		print('Server: File sent')

	def handleQUIT(self, arg):
		self.client.sendMsgData(b"221 Good Bye.\r\n")
	 
	def commandManagement(self):
		#self.fileSystem.resetPath()
		self.client.sendMsgData(b"220 FTP Server by GrzRo. Hello.\r\n") # welcome client
		 
		while self.client.isMsgConnOpen():
			try:
				self.data = self.client.recvMsg()
			except:
				print('Server: waiting for client')
				return
		 
			cmd, arg = str(self.data, "utf-8").replace('\r\n', ' ').split(' ', 1)
			arg = arg.rstrip() # delete last char which is ' '
			cmd = cmd.upper()

			print("Client: {} {}".format(cmd, arg))

			if cmd in self.methods:
				self.methods[cmd](arg)
			else:
				print("Server: Unknown method: " + cmd + " " + arg)

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
			print("Server: Waiting for connections on port: {}".format(port))
			self.client.acceptMsgConn()
			self.commandManagement()
		
if __name__ == '__main__':
	HOST = '127.0.0.1'
	PORT = 5022

	srv = ConnHandler()
	srv.establish(PORT)
