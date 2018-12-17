import time


class Interval(object):
    def __init__(self):
        self.daemon_alive = True
        self.thread = None # keep a reference to the thread so that we can "join"

    def ticktock(self, interval, func):
        while self.daemon_alive:
            time.sleep(interval)
            func()


