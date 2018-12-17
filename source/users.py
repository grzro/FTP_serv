import json

class Users:
	def __init__(self, json_str):
		try:
			self.usrsData = json.loads(json_str)
		except json.JSONDecodeError:
			raise Exception
			return

	def checkUser(self, userName):
		try:
			if self.usrsData['users'][userName] is not None:
				return True
		except:
			return False

	def checkPassword(self, userName, passw):
		if self.checkUser(userName):
			if self.usrsData['users'][userName] == passw:
				return True

		else:
			return False

	def printUsrs(self):
		print(self.usrsData)