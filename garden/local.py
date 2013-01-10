from twisted.internet import defer



class LocalWorkDispatcher(object):
    """
    I dispatch work to local workers.
    """
    
    
    def __init__(self, worker):
        self.worker = worker
        self.result_receiver = lambda *a: None


    def __call__(self, entity, name, version, lineage, inputs, input_hashes):
        d = self.worker.run(name, version, inputs)
        d.addCallback(self._gotResult, entity, name, version, lineage,
                      inputs, input_hashes)
        return defer.succeed(True)


    def _gotResult(self, result, entity, name, version, lineage, inputs,
                   input_hashes):
        self.result_receiver(entity, name, version, lineage, result,
                             inputs, input_hashes)


    def sendResultsTo(self, func):
        self.result_receiver = func



class LocalWorker(object):
    """
    I am a worker that executes python functions within the current thread.
    """
    
    def __init__(self):
        self._functions = {}
    
    
    def addFunction(self, name, version, func):
        """
        @param name: Destination name
        @param version: Destination version
        @param func: Function to run
        """
        self._functions[(name, version)] = func


    def run(self, name, version, args):
        """
        XXX
        """
        func = self._functions[(name, version)]
        return defer.succeed(func(*args))



class InMemoryStore(object):
    """
    I hold entity data in memory.
    """


    def __init__(self):
        self._data = []


    def get(self, entity, name, version):
        r = [x for x in self._data if x[:3] == (entity, name, version)]
        return defer.succeed(r)


    def put(self, entity, name, version, lineage, value):
        self._data.append((entity, name, version, lineage, value))
        return defer.succeed({'changed': True})


