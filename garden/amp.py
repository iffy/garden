"""
AMP clients and servers
"""

from twisted.protocols import amp
from twisted.internet import defer
from zope.interface import implements

from garden.interface import IWorkSender, IWorkReceiver, IResultSender



class DoWork(amp.Command):

    arguments = [
        ('entity', amp.String()),
        ('name', amp.String()),
        ('version', amp.String()),
        ('lineage', amp.String()),
        ('inputs', amp.ListOf(amp.ListOf(amp.String()))),
    ]
    response = []


class WorkSender(amp.AMP):
    
    
    implements(IWorkSender)


    def sendWork(self, entity, name, version, lineage, inputs):
        return self.callRemote(DoWork, entity=entity, name=name,
                               version=version, lineage=lineage,
                               inputs=[list(x) for x in inputs])



class WorkReceiver(amp.AMP):


    implements(IWorkReceiver)


    worker = None


    @DoWork.responder
    def receiveWork(self, entity, name, version, lineage, inputs):
        r = self.worker.doWork(entity, name, version, lineage, inputs)
        return r.addCallback(lambda x: {})



class ResultSender(amp.AMP):


    implements(IResultSender)




