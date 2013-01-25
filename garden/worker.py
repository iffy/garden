from zope.interface import implements
from twisted.internet import threads

from garden.interface import IWorker



def _makeResultInputs(inputs):
    """
    Given a list of work inputs, convert it to a list of result/error inputs.
    This essentially just means stripping out the value.
    """
    # XXX I don't like these magic numbers
    return [tuple(x[:3]) + (x[4],) for x in inputs]


def _getInputValues(inputs):
    """
    Given a list of work inputs, return a list of just the values
    """
    # XXX I don't like this magic number
    return [x[3] for x in inputs]



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
        args = _getInputValues(inputs)
        value_stripped_inputs = _makeResultInputs(inputs)
        try:
            result = func(*args)
            return self.result_receiver.resultReceived(entity, name, version,
                lineage, result, value_stripped_inputs)
        except Exception as e:
            return self.error_receiver.resultErrorReceived(entity, name,
                version, lineage, repr(e), value_stripped_inputs)


    def setResultReceiver(self, receiver):
        """
        XXX
        """
        self.result_receiver = receiver


    def setResultErrorReceiver(self, receiver):
        self.error_receiver = receiver



class ThreadedWorker(object):
    """
    I do work in threads, rather than blocking the main thread.
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


    def setResultReceiver(self, receiver):
        """
        XXX
        """
        self.result_receiver = receiver


    def setResultErrorReceiver(self, receiver):
        self.error_receiver = receiver


    def workReceived(self, entity, name, version, lineage, inputs):
        """
        XXX
        """
        func = self._functions[(name, version)]
        args = _getInputValues(inputs)
        value_stripped_inputs = _makeResultInputs(inputs)
        
        result = threads.deferToThread(func, *args)
        
        def gotResult(result, value_stripped_inputs):
            return self.result_receiver.resultReceived(entity, name, version,
                lineage, result, value_stripped_inputs)
        
        def gotError(err, value_stripped_inputs):
            return self.error_receiver.resultErrorReceived(entity, name,
                version, lineage, repr(err.value), value_stripped_inputs)
        
        return result.addCallbacks(gotResult, gotError,
                                   callbackArgs=(value_stripped_inputs,),
                                   errbackArgs=(value_stripped_inputs,))



