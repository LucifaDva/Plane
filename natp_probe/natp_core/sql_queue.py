import threading
import Queue

class sql_queue:
    def __init__(self, max_size=0):
        # if max_size is 0, the queue size is infinite
        self.__queue = Queue.Queue(max_size)
        self.lock = threading.Lock()

    def put(self, data):
        self.lock.acquire()
        self.__queue.put(data)
        self.lock.release()

    def get(self):
        self.lock.acquire()
        data = self.__queue.get()
        self.lock.release()
        return data
    
    def empty(self):
        return self.__queue.empty()