from twisted.internet import defer

from zope.interface import implements

from garden.interface import (IWorkSender, IWorkReceiver, IResultSender,
                              IResultReceiver)



class LocalDispatcher(object):
    """
    I send work between the L{IGardener} and L{IWorker}s and send results back
    to the L{IGardener}.
    """
    
    implements(IWorkSender, IWorkReceiver, IResultSender, IResultReceiver)
    
    worker = None
    gardener = None
    
    
    def __init__(self, worker):
        self.worker = worker
        self.result_receiver = lambda *a: None


    def sendWork(self, entity, name, version, lineage, inputs):
        """
        XXX
        """
        return self.worker.doWork(entity, name, version, lineage, inputs)


    def sendResult(self, entity, name, version, lineage, value, inputs):
        """
        XXX
        """
        return self.gardener.workReceived(entity, name, version, lineage, value,
                                          inputs)


    def sendError(self, entity, name, version, lineage, error, inputs):
        """
        XXX
        """
        return self.gardener.workErrorReceived(entity, name, version, lineage,
                                               error, inputs)



class InMemoryStore(object):
    """
    I hold entity data in memory.
    """


    def __init__(self):
        self._data = {}


    def get(self, entity, name, version):
        keys = [x for x in self._data if x[:3] == (entity, name, version)]
        return defer.succeed([k + (self._data[k],) for k in keys])


    def put(self, entity, name, version, lineage, value):
        self._data[(entity, name, version, lineage)] = value
        return defer.succeed({'changed': True})


