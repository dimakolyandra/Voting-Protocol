

class RunningCommandException(BaseException):

    def __init__(self):
        RunningCommandException.text = "Server can not do this task"
