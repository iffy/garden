"""
AMP clients and servers
"""

from twisted.protocols import amp
from twisted.internet import defer, protocol
from zope.interface import implements

from garden.interface import IWorkSender, IWorkReceiver, IResultSender
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

    pass



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
        r = self.worker.doWork(entity, name, version, lineage, inputs)
        return r.addCallback(lambda x: {})



class ResultSender(amp.AMP):


    implements(IResultSender)


    def _sendResult(self, entity, name, version, lineage, value, inputs,
                    is_error=False):
        return self.callRemote(ReceiveResult, entity=entity, name=name,
                        version=version, lineage=lineage, value=value,
                        is_error=is_error,
                        inputs=[list(x) for x in inputs])


    def sendResult(self, entity, name, version, lineage, value, inputs):
        """
        XXX
        """
        return self._sendResult(entity, name, version, lineage, value, inputs)
        


    def sendError(self, entity, name, version, lineage, error, inputs):
        """
        XXX
        """
        return self._sendResult(entity, name, version, lineage, error, inputs,
                                is_error=True)





