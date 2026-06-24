from PyQt6.QtCore import QThread, pyqtSignal

from utils.global_events import event_bus


class EventWorker(QThread):

    event_received = pyqtSignal(str)

    def run(self):

        while True:

            message = event_bus.get()

            self.event_received.emit(
                message
            )