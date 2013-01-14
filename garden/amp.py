"""
AMP clients and servers
"""

from twisted.protocols import amp
from twisted.internet import defer, protocol
from zope.interface import implements

from garden.interface import (IWorkSender, IWorkReceiver, IResultSender,
                              IResultReceiver)
from garden.util import RoundRobinChooser



class NoWorkerAvailable(Exception):
    pass



class DoWork(amp.Command):

    arguments = [
        ('entity', amp.String()),
        ('name', amp.String()),
        ('version', amp.String()),
        ('lineage', amp.String()),
        ('inputs', amp.ListOf(amp.ListOf(amp.String()))),
    ]
    response = []



class ReceiveResult(amp.Command):

    arguments = [
        ('entity', amp.String()),
        ('name', amp.String()),
        ('version', amp.String()),
        ('lineage', amp.String()),
        ('value', amp.String()),
        ('inputs', amp.ListOf(amp.ListOf(amp.String()))),
    ]
    response = []



class ReceiveError(amp.Command):

    arguments = [
        ('entity', amp.String()),
        ('name', amp.String()),
        ('version', amp.String()),
        ('lineage', amp.String()),
        ('error', amp.String()),
        ('inputs', amp.ListOf(amp.ListOf(amp.String()))),
    ]
    response = []



class WorkSenderProtocol(amp.AMP):
    """
    XXX
    """
    
    
    implements(IWorkSender)


    def sendWork(self, entity, name, version, lineage, inputs):
        return self.callRemote(DoWork, entity=entity, name=name,
                               version=version, lineage=lineage,
                               inputs=[list(x) for x in inputs])


    def connectionMade(self):
        amp.AMP.connectionMade(self)
        self.factory._protocolConnected(self)


    def connectionLost(self, reason):
        self.factory._protocolDisconnected(self)
        amp.AMP.connectionLost(self, reason)



class WorkSender(protocol.Factory):
    """
    XXX
    """
    
    implements(IWorkSender)
    
    protocol = WorkSenderProtocol


    def __init__(self):
        self.proto_chooser = RoundRobinChooser()
        self.connected_protocols = []


    def _protocolConnected(self, proto):
        self.proto_chooser.add(proto)


    def _protocolDisconnected(self, proto):
        self.proto_chooser.remove(proto)


    def sendWork(self, entity, name, version, lineage, inputs):
        try:
            proto = self.proto_chooser.next()
        except:
            return defer.fail(NoWorkerAvailable('something'))
        return proto.sendWork(entity, name, version, lineage, inputs)



class WorkReceiver(amp.AMP):
    """
    XXX
    """


    implements(IWorkReceiver)


    worker = None


    @DoWork.responder
    def receiveWork(self, entity, name, version, lineage, inputs):
        """
        XXX
        """
        r = self.worker.doWork(entity, name, version, lineage, inputs)
        return r.addCallback(lambda x: {})



class ResultSender(amp.AMP):
    """
    XXX
    """


    implements(IResultSender)


    def sendResult(self, entity, name, version, lineage, value, inputs):
        """
        XXX
        """
        return self.callRemote(ReceiveResult, entity=entity, name=name,
                        version=version, lineage=lineage, value=value,
                        inputs=[list(x) for x in inputs])
        


    def sendError(self, entity, name, version, lineage, error, inputs):
        """
        XXX
        """
        return self.callRemote(ReceiveError, entity=entity, name=name,
                        version=version, lineage=lineage, error=error,
                        inputs=[list(x) for x in inputs])



class ResultReceiverProtocol(amp.AMP):
    """
    XXX
    """


    @ReceiveResult.responder
    def receiveResult(self, entity, name, version, lineage, value, inputs):
        """
        XXX
        """
        r = self.factory.gardener.workReceived(entity, name, version, lineage,
            value, inputs)
        return r.addCallback(lambda x: {})


    @ReceiveError.responder
    def receiveError(self, entity, name, version, lineage, error, inputs):
        """
        XXX
        """
        r = self.factory.gardener.workErrorReceived(entity, name, version,
            lineage, error, inputs)
        return r.addCallback(lambda x: {})



class ResultReceiver(protocol.Factory):
    """
    XXX
    """
    
    
    implements(IResultReceiver)

    gardener = None
    protocol = ResultReceiverProtocol
    


