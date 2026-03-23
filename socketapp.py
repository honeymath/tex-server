from flask_socketio import SocketIO

socketio = SocketIO()  # do not pass app here yet!
state = {} ## this declares a global state dictionary

#ai:you may modify the following
import uuid
from threading import Event

responses = {}  # Stores all response objects by UUID

class Response:
    def __init__(self):
        self.uuid = str(uuid.uuid4())
        responses[self.uuid] = self
        self.event = Event()
        self._result = []

    def unlock(self):
        self.event.set()

    @property
    def result(self):
        return self._result[-1] if self._result else None

    @result.setter
    def result(self, value):
        self._result.append(value)
#end
