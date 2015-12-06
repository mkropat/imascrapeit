import threading

class BackgroundRunner:
    def __init__(self):
        self._threads = []

    def run(self, runnable, *args, **kwargs):
        t = threading.Thread(target=runnable, args=args, kwargs=kwargs)
        self._threads.append(t)
        t.start()

    def join(self):
        for t in self._threads:
            t.join()

