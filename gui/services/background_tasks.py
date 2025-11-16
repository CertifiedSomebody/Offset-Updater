from PyQt6.QtCore import QThread, pyqtSignal


class BackgroundTask(QThread):
    """
    Generic threaded background task.
    Run heavy logic here to keep UI responsive.
    """

    progress = pyqtSignal(int)        # emit 0–100
    finished = pyqtSignal(object)     # result object
    error = pyqtSignal(str)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
