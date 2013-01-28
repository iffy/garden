from zope.interface import implements
from twisted.internet import threads

from garden.interface import ISource, IWorker, IWork, IResult, IResultError


def _getInputValues(inputs):
    """
    Given a list of work inputs, return a list of just the values
    """
    return [x.value for x in inputs]



class BlockingWorker(object):
    """
    I run work functions in the main thread.
    """
    
    implements(IWorker)
    sourceInterfaces = IResult, IResultError
    
    
    def __init__(self):
        self._functions = {}


    def receiverMapping(self):
        """
        XXX
        """
        return {
            IWork: self.workReceived,
        }
    
    
    def registerFunction(self, name, version, func):
        """
        Register a function to compute a destination.
        
        @param name: Destination name
        @param version: Destination version
        
        @param func: Function to run
        """
        self._functions[(name, version)] = func


    def workReceived(self, work):
        """
        XXX
        """
        func = self._functions[(work.name, work.version)]
        args = _getInputValues(work.inputs)
        try:
            result = func(*args)
            return ISource(self).emit(work.toResult(result))
        except Exception as e:
            return ISource(self).emit(work.toResultError(repr(e)))



class ThreadedWorker(object):
    """
    I do work in threads, rather than blocking the main thread.
    """
    
    implements(IWorker)
    sourceInterfaces = IResult, IResultError


    def __init__(self):
        self._functions = {}


    def receiverMapping(self):
        """
        XXX
        """
        return {
            IWork: self.workReceived,
        }

    
    def registerFunction(self, name, version, func):
        """
        Register a function to compute a destination.
        
        @param name: Destination name
        @param version: Destination version
        
        @param func: Function to run
        """
        self._functions[(name, version)] = func


    def workReceived(self, work):
        """
        XXX
        """
        func = self._functions[(work.name, work.version)]
        args = _getInputValues(work.inputs)
        
        result = threads.deferToThread(func, *args)
        
        def gotResult(result, work):
            return work.toResult(result)
        
        def gotError(err, work):
            return work.toResultError(repr(err.value))
        
        def send(response):
            return ISource(self).emit(response)
        
        d = result.addCallbacks(gotResult, gotError,
                                callbackArgs=(work,),
                                errbackArgs=(work,),)
        return d.addBoth(send)



