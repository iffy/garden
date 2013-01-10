class LocalWorkDispatcher(object):
    """
    I dispatch work to local workers.
    """
    
    
    def __init__(self, worker):
        self.worker = worker



class LocalWorker(object):
    """
    I am a worker that can only execute python functions within the current
    process.
    """
    
    
    def addFunction(self, name, version, func):
        """
        @param name: Destination name
        @param version: Destination version
        @param func: Function to run
        """



class InMemoryStore(object):
    """
    I hold entity data in memory.
    """


    def __init__(self):
        self._data = []


    def get(self, entity, name, version):
        return [x for x in self._data if x[:3] == (entity, name, version)]            


    def put(self, entity, name, version, lineage, value):
        self._data.append((entity, name, version, lineage, value))


