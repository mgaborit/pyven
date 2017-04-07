class Parallelizer(object):
    
    def __init__(self, threads=[], max_concurrent=1):
        if max_concurrent > 4:
            max_concurrent = 4
        self.max_concurrent = max_concurrent
        self.threads = threads
        
    def run(self):
        if len(self.threads) > 0:
            i = 0
            running = []
            while i < len(self.threads):
                if len(running) < self.max_concurrent:
                    running.append(self.threads[i])
                    self.threads[i].start()
                    i += 1
                running = [t for t in running if t.is_alive()]
            for t in running:
                t.join()
                    