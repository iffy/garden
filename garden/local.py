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