

class QuitException(Exception):
    pass

class ConnectionException(Exception):
    def __init__(self, msg):
        self.msg = msg

class DecodeError(Exception):
    def __init__(self, msg):
        self.msg = msg