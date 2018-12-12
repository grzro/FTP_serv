import socket

class ConnectionManager:
	def bindMsgConn(self, ip: tuple, port: int):
		self.host = ip
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind((self.host, port))
		self.isMsgSockOpen = False

	def bindDTConn(self, port: int):
		if not self.host:
			print('First bind MSG socket! ( bindMsgConn() )')
			return
		self.sData = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sData.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sData.bind((self.host, port))

	def listenMsgConn(self):
		self.s.listen(1)

	def listenDTConn(self):
		self.sData.listen(1)

	def acceptMsgConn(self):
		self.msgConn, self.addr = self.s.accept()
		print('Connected by', self.addr)
		self.s.settimeout(120)
		self.isMsgSockOpen = True

	def acceptDTConn(self):
		self.dataConn, self.addrData = self.sData.accept()

	def getDTConnInfo(self):
		return (self.host, self.sData.getsockname()[1])

	def sendMsgData(self, data):
		self.msgConn.sendall(data)

	def sendDTData(self, data):
		self.dataConn.sendall(data)

	def recvMsg(self):
		data = b''
		while True:
			data += self.msgConn.recv(1)
 
			if data == b'':
				raise Exception("disconnected")
	 
			elif b'\r\n' in data:
				break
 
		return data

	def isMsgConnOpen(self):
		return self.isMsgSockOpen

	def closeDTConn(self):
		self.dataConn.shutdown(socket.SHUT_RDWR)
		self.dataConn.close()

	def closeMsgConn(self):
		#self.s.shutdown(socket.SHUT_RDWR)
		#self.s.close()
		pass