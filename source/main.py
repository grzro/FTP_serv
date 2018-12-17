import files
import connection_manager
import users
import os

class ConnHandler:

	def handleUSER(self, arg):
		if self.user.checkUser(arg):
			self.loggingUsr = arg
			self.client.sendMsgData(b"331 User name ok, need password.\r\n")
		else:
			self.loggingUsr = ''
			self.client.sendMsgData(b"332 Need account for login.\r\n")
			print("Server: unrezognized user: " + arg)

	def handlePASS(self, arg):
		if self.user.checkPassword(self.loggingUsr, arg):
			self.client.sendMsgData(b"230 User logged in.\r\n")
		else:
			self.loggingUsr = ''
			self.client.sendMsgData(b"530 Invalid password.\r\n")
			print("Server: invalid password")

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
		FF works with everything
		TotalCommander with current path
		FileZilla must start from '/'
		Chrome need to have costant path here f.eg. 'home', no matter on which dir it is operating
		'''
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

	def handleCDUP(self, arg):
		currPath = self.fileSystem.getdir()
		dirs = currPath.split('\\')
		del dirs[len(dirs) - 1] # remove last dir name
		newPath = '\\'.join(dirs)
		if self.fileSystem.validatePath(newPath):
			self.fileSystem.chdir(newPath) # <-- raises exception
			self.client.sendMsgData(b"250 Requested file action completed.\r\n")
		else:
			self.client.sendMsgData(b"550 File not found.\r\n")
			print('Server: Invalid path: ' + newPath)

	def handleMKD(self, dirName):
		try:
			self.fileSystem.mkdir(dirName)
		except:
			self.client.sendMsgData(b"550 Requested action not taken.\r\n")
			print('Server: Can not create directory: ' + dirName)
			return

		self.client.sendMsgData(b"257 Directory created\r\n")

		#remove directory
	def handleRMD(self, dirName):
		try:
			self.fileSystem.remdir(dirName)
		except:
			self.client.sendMsgData(b"550 Requested action not taken.\r\n")
			print('Server: Can not remove directory: ' + dirName)
			return

		self.client.sendMsgData(b"257 Requested file action ok.\r\n")

		#delete file
	def handleDELE(self, fileName):
		try:
			self.fileSystem.deleteFile(fileName)
		except:
			self.client.sendMsgData(b"550 Requested action not taken.\r\n")
			print('Server: Can not delete file: ' + fileName)
			return

		self.client.sendMsgData(b"250 Requested file action ok.\r\n")

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

	# it is used to validate if received file has the same size as original
	def handleSIZE(self, fName):
		fSize = self.fileSystem.getFileSize(fName)
		reply = "550 {}\r\n".format(fSize)
		self.client.sendMsgData(bytes(reply, "utf-8"))

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

	def handleSTOR(self, fName):
		self.client.sendMsgData(b"125 Data connection already open.\r\n")
		
		self.client.acceptDTConn()
		data = self.client.recvDTData()
		self.client.closeDTConn()

		try:
			self.fileSystem.storeFile(fName, data)
		except:
			self.client.sendMsgData(b"451 Requested action aborted: local error in processing.\r\n")
			print('Server: Can not create file: ' + fName)
			return

		self.client.sendMsgData(b"226 Transfer complete\r\n")
		print('Server: File saved: ' + fName)

	def handleRNFR(self, arg):
		self.renameFrom = arg
		self.client.sendMsgData(b"350 Requested file action pending further information.\r\n")

	def handleRNTO(self, arg):
		try:
			self.fileSystem.rename(self.renameFrom, arg)
		except:
			self.client.sendMsgData(b"553 Can not rename file.\r\n")
			print("Server: Can not rename file " + self.renameFrom + " to " + arg)
			return
		self.client.sendMsgData(b"250 File renamed.\r\n")
		print("Server: File " + self.renameFrom + " renamed to " + arg)

	def handleQUIT(self, arg):
		self.client.sendMsgData(b"221 Good Bye.\r\n")

	def sendWelcomeMsg(self):
		self.client.sendMsgData(b"220 FTP Server by GrzRo. Hello.\r\n")
	 
	def commandManagement(self):
		self.sendWelcomeMsg()
		 
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
		usrFileData = self.fileSystem.loadUsersFile("users.txt")
		self.user = users.Users(usrFileData)

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
