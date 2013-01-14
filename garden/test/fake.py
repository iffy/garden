"""
A collection of verified fakes for testing.
"""

__all__ = ['FakeResultReceiver', 'FakeWorkReceiver', 'FakeWorker',
           'FakeGardener']

from zope.interface import implements
from twisted.internet import defer

from mock import create_autospec

from garden.interface import IResultReceiver, IWorkReceiver, IWorker, IGardener



class _SpeccedMock(object):

    faked_methods = []

    def __init__(self):
        for method, ret in self.faked_methods:
            setattr(self, method, create_autospec(getattr(self, method),
                    side_effect=ret))



class FakeResultReceiver(_SpeccedMock):
    
    
    implements(IResultReceiver)
    
    
    faked_methods = [
        ('resultErrorReceived', lambda *x: defer.succeed('received')),
        ('resultReceived', lambda *x: defer.succeed('received')),
    ]


    def resultErrorReceived(self, entity, name, version, lineage, error, inputs):
        pass


    def resultReceived(self, entity, name, version, lineage, value, inputs):
        pass



class FakeWorkReceiver(_SpeccedMock):


    implements(IWorkReceiver)
    
    faked_methods = [
        ('workReceived', lambda *x: defer.succeed('sent')),
    ]


    def workReceived(self, entity, name, version, lineage, inputs):
        pass



class FakeWorker(_SpeccedMock):


    implements(IWorker)
    
    faked_methods = [
        ('workReceived', lambda *x: defer.succeed('received')),
    ]
    
    result_receiver = None


    def workReceived(self, entity, name, version, lineage, inputs):
        pass


    def setResultReceiver(self, receiver):
        self.result_receiver = receiver



class FakeGardener(_SpeccedMock):


    implements(IGardener)
    
    faked_methods = [
        ('inputReceived', lambda *x: defer.succeed('done')),
        ('resultReceived', lambda *x: defer.succeed('done')),
        ('resultErrorReceived', lambda *x: defer.succeed('done')),
    ]
    
    
    work_receiver = None
    
    
    def inputReceived(self, entity, name, version, value):
        pass


    def resultReceived(self, entity, name, version, lineage, value, inputs):
        pass


    def resultErrorReceived(self, entity, name, version, lineage, error, inputs):
        pass


    def setWorkReceiver(self, receiver):
        self.work_receiver = receiver






