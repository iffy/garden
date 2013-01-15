from zope.interface import implements

from garden.interface import IWorker



class BlockingWorker(object):
    """
    I run work functions in the main thread.
    """
    
    implements(IWorker)
    
    result_receiver = None
    
    
    def __init__(self):
        self._functions = {}
    
    
    def registerFunction(self, name, version, func):
        """
        Register a function to compute a destination.
        
        @param name: Destination name
        @param version: Destination version
        
        @param func: Function to run
        """
        self._functions[(name, version)] = func


    def workReceived(self, entity, name, version, lineage, inputs):
        """
        XXX
        """
        func = self._functions[(name, version)]
        args = [x[3] for x in inputs]
        result = func(*args)
        value_stripped_inputs = [tuple(x[:3]) + (x[4],) for x in inputs]
        return self.result_receiver.resultReceived(entity, name, version,
            lineage, result, value_stripped_inputs)


    def setResultReceiver(self, receiver):
        """
        XXX
        """
        self.result_receiver = receiver