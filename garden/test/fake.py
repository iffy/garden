"""
A collection of verified fakes for testing.
"""

__all__ = ['FakeResultSender', 'FakeWorkSender', 'FakeWorker']

from zope.interface import implements
from twisted.internet import defer

from mock import create_autospec

from garden.interface import IResultSender, IWorkSender, IWorker, IGardener



class _SpeccedMock(object):

    faked_methods = []

    def __init__(self):
        for method, ret in self.faked_methods:
            setattr(self, method, create_autospec(getattr(self, method),
                    side_effect=ret))



class FakeResultSender(_SpeccedMock):
    
    
    implements(IResultSender)
    
    
    faked_methods = [
        ('sendError', lambda *x: defer.succeed('sent')),
        ('sendResult', lambda *x: defer.succeed('sent')),
    ]


    def sendError(self, entity, name, version, lineage, error, inputs):
        pass


    def sendResult(self, entity, name, version, lineage, value, inputs):
        pass



class FakeWorkSender(_SpeccedMock):


    implements(IWorkSender)
    
    faked_methods = [
        ('sendWork', lambda *x: defer.succeed('sent')),
    ]


    def sendWork(self, entity, name, version, lineage, inputs):
        pass



class FakeWorker(_SpeccedMock):


    implements(IWorker)
    
    faked_methods = [
        ('doWork', lambda *x: defer.succeed('done')),
    ]


    sender = None

    def doWork(self, entity, name, version, lineage, inputs):
        pass



class FakeGardener(_SpeccedMock):


    implements(IGardener)
    
    faked_methods = [
        ('inputReceived', lambda *x: defer.succeed('done')),
        ('workReceived', lambda *x: defer.succeed('done')),
    ]
    
    
    work_sender = None
    
    
    def inputReceived(self, entity, name, version, value):
        pass


    def workReceived(self, entity, name, version, lineage, value, inputs):
        pass






