"""
AMP clients and servers
"""

from twisted.protocols import amp
from twisted.internet import defer, protocol
from zope.interface import implements

from garden.interface import (IWorkSource, IWorkReceiver, IResultSource,
                              IResultReceiver, IResultErrorSource,
                              IResultErrorReceiver)
from garden.util import RoundRobinChooser



class NoWorkerAvailable(Exception):
    pass



class ReceiveWork(amp.Command):

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



class GardenerProtocol(amp.AMP):
    """
    XXX
    """
    
    implements(IWorkReceiver, IResultSource, IResultReceiver,
        IResultErrorSource, IResultErrorReceiver)
    
    result_receiver = None


    def connectionMade(self):
        amp.AMP.connectionMade(self)
        self.factory._protocolConnected(self)


    def connectionLost(self, reason):
        self.factory._protocolDisconnected(self)
        amp.AMP.connectionLost(self, reason)


    def workReceived(self, entity, name, version, lineage, inputs):
        """
        XXX
        """
        return self.callRemote(ReceiveWork,
            entity=entity,
            name=name,
            version=version,
            lineage=lineage,
            inputs=[list(x) for x in inputs])


    def setResultReceiver(self, receiver):
        """
        XXX
        """
        self.result_receiver = receiver


    def setResultErrorReceiver(self, receiver):
        self.error_receiver = receiver


    @ReceiveResult.responder
    def resultReceived(self, entity, name, version, lineage, value, inputs):
        """
        XXX
        """
        result = self.result_receiver.resultReceived(entity, name, version,
            lineage, value, inputs)
        return result.addCallback(lambda x: {})


    @ReceiveError.responder
    def resultErrorReceived(self, entity, name, version, lineage, error, inputs):
        """
        XXX
        """
        result = self.error_receiver.resultErrorReceived(entity, name, version,
            lineage, error, inputs)
        return result.addCallback(lambda x: {})



class GardenerFactory(protocol.Factory):
    """
    I reside with the L{Gardener} and communicate with L{WorkerFactory}s.
    """
    
    implements(IWorkReceiver, IResultSource, IResultReceiver,
        IResultErrorReceiver, IResultErrorSource)

    protocol = GardenerProtocol
    result_receiver = None


    def __init__(self):
        self.proto_chooser = RoundRobinChooser()
        self.connected_protocols = []


    def _protocolConnected(self, proto):
        self.proto_chooser.add(proto)


    def _protocolDisconnected(self, proto):
        self.proto_chooser.remove(proto)


    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.factory = self
        proto.setResultReceiver(self)
        proto.setResultErrorReceiver(self)
        return proto


    def workReceived(self, entity, name, version, lineage, inputs):
        try:
            proto = self.proto_chooser.next()
        except:
            return defer.fail(NoWorkerAvailable('something'))
        return proto.workReceived(entity, name, version, lineage, inputs)


    def setResultReceiver(self, receiver):
        self.result_receiver = receiver


    def setResultErrorReceiver(self, receiver):
        self.error_receiver = receiver


    def resultReceived(self, entity, name, version, lineage, value, inputs):
        return self.result_receiver.resultReceived(entity, name, version,
            lineage, value, inputs)


    def resultErrorReceived(self, entity, name, version, lineage, value, inputs):
        return self.error_receiver.resultErrorReceived(entity, name, version,
            lineage, value, inputs)



class WorkerProtocol(amp.AMP):
    """
    XXX
    """
    
    implements(IWorkReceiver, IWorkSource, IResultReceiver, IResultErrorReceiver)
    
    work_receiver = None

    
    def connectionMade(self):
        amp.AMP.connectionMade(self)
        self.factory.connected_protocol = self


    def connectionLost(self, reason):
        self.factory.connected_protocol = None
        amp.AMP.connectionLost(self, reason)


    def setWorkReceiver(self, receiver):
        self.work_receiver = receiver


    @ReceiveWork.responder
    def workReceived(self, entity, name, version, lineage, inputs):
        return self.work_receiver.workReceived(entity, name, version, lineage,
                                               inputs).addCallback(lambda x:{})


    def resultReceived(self, entity, name, version, lineage, value, inputs):
        return self.callRemote(ReceiveResult,
            entity=entity,
            name=name,
            version=version,
            lineage=lineage,
            value=value,
            inputs=inputs)


    def resultErrorReceived(self, entity, name, version, lineage, error, inputs):
        return self.callRemote(ReceiveError,
            entity=entity,
            name=name,
            version=version,
            lineage=lineage,
            error=error,
            inputs=inputs)



class WorkerFactory(protocol.ReconnectingClientFactory):
    """
    XXX
    """
    
    implements(IWorkReceiver, IWorkSource, IResultReceiver, IResultErrorReceiver)
    
    protocol = WorkerProtocol
    work_receiver = None
    connected_protocol = None
    
    
    def buildProtocol(self, addr):
        proto = self.protocol()
        proto.factory = self
        proto.setWorkReceiver(self)
        return proto
    
    
    def setWorkReceiver(self, receiver):
        self.work_receiver = receiver


    def workReceived(self, entity, name, version, lineage, inputs):
        return self.work_receiver.workReceived(entity, name, version, lineage,
            inputs)


    def resultReceived(self, entity, name, version, lineage, value, inputs):
        return self.connected_protocol.resultReceived(entity, name, version,
            lineage, value, inputs)


    def resultErrorReceived(self, entity, name, version, lineage, error, inputs):
        return self.connected_protocol.resultErrorReceived(entity, name, version,
            lineage, error, inputs)



class WorkSenderProtocol(amp.AMP):
    """
    I receive work and send it over the wire to a L{WorkSource}.
    """


    def sendWork(self, entity, name, version, lineage, inputs):
        return self.callRemote(ReceiveWork, entity=entity, name=name,
                               version=version, lineage=lineage,
                               inputs=[list(x) for x in inputs])


    def connectionMade(self):
        amp.AMP.connectionMade(self)
        self.factory._protocolConnected(self)


    def connectionLost(self, reason):
        self.factory._protocolDisconnected(self)
        amp.AMP.connectionLost(self, reason)



