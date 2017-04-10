class NagiosResponse:
	_msgBagWarning = []
	_msgBagCritical = []
	_code = None

	OK = 0
	WARNING = 1
	CRITICAL = 2
	UNKNOWN = 3

	def __init__(self):
		self._code = self.OK

	
	def writeWarningMessage(self, msg):
		self._msgBagWarning.append(msg)

	def writeCriticalMessage(self, msg):
		self._msgBagCritical.append(msg)

	
	def setCode(self, code):
		self._code = code

	def getCode(self):
		return self._code

	def getMsg(self):
		if self._code == self.WARNING:
			return self._msgBagWarning
		elif self._code == self.CRITICAL:
			return self._msgBagCritical
		else:
			return "OK"

