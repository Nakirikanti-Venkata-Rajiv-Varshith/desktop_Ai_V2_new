from queue import Queue


class EventBus:

    def __init__(self):
        self.queue = Queue()

    def emit(self, message):
        self.queue.put(message)

    def get(self):
        return self.queue.get()

    def empty(self):
        return self.queue.empty()