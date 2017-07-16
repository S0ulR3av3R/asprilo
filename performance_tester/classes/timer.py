import time

class Timer(object):
    def __init__(self):
        self.accuTime = 0
        self.running = False

    def start(self):
        self.start_time = time.time()
        self.running = True
        return self

    def stop(self):
        if self.running:
            self.end_time = time.time()
            self.lastsecs = self.end_time - self.start_time
            self.accuTime = self.accuTime + self.lastsecs
            self.running = False
            return self.lastsecs
        return 0
            
    def getLastSecs(self):
        return self.lastsecs
        
    def getAccuTime(self):
        return self.accuTime
        
    def reset(self):
        self.accuTime = 0
        self.running = False

