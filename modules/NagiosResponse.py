class NagiosResponse:
    _msgBagWarning = []
    _msgBagCritical = []
    _okMsg = ""
    _code = None

    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

    def __init__(self, ok_msg=""):
        self._code = self.OK
        self._okMsg = ok_msg


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
            return "WARNING - " + self._toString(self._msgBagWarning)
        elif self._code == self.CRITICAL:
            return "CRITICAL - " + self._toString(self._msgBagCritical)
        elif self._code == self.OK:
            return "OK - " + self._okMsg if self._okMsg else "OK"
        else:
            return "UNKNOWN!"

    def _toString(self, msgArray):
        return ' | '.join(msgArray)

