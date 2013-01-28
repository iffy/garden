"""
A collection of verified fakes for testing.
"""

__all__ = ['FakeResultReceiver', 'FakeWorkReceiver', 'FakeWorker',
           'FakeGardener', 'FakeDataReceiver', 'FakeInputReceiver']

from zope.interface import implements
from twisted.internet import defer

from mock import create_autospec

from garden.interface import (IResultReceiver, IWorkReceiver, IWorker,
                              IGardener, IInputReceiver, IDataReceiver,
                              IResultErrorReceiver)



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


    def resultErrorReceived(self, error):
        pass


    def resultReceived(self, result):
        pass



class FakeWorkReceiver(_SpeccedMock):


    implements(IWorkReceiver)
    
    faked_methods = [
        ('workReceived', lambda *x: defer.succeed('received')),
    ]


    def workReceived(self, work):
        pass



class FakeWorker(_SpeccedMock):


    implements(IWorker)
    
    faked_methods = [
        ('workReceived', lambda *x: defer.succeed('received')),
        ('setResultErrorReceiver', lambda *x: None),
    ]
    
    result_receiver = None


    def workReceived(self, work):
        pass


    def setResultReceiver(self, receiver):
        self.result_receiver = receiver


    def setResultErrorReceiver(self, receiver):
        pass



class FakeGardener(_SpeccedMock):


    implements(IGardener)
    
    faked_methods = [
        ('inputReceived', lambda *x: defer.succeed('done')),
        ('resultReceived', lambda *x: defer.succeed('done')),
        ('resultErrorReceived', lambda *x: defer.succeed('done')),
    ]
    
    
    work_receiver = None
    
    
    def inputReceived(self, data):
        pass


    def resultReceived(self, result):
        pass


    def resultErrorReceived(self, error):
        pass


    def setWorkReceiver(self, receiver):
        self.work_receiver = receiver


    def setDataReceiver(self, receiver):
        self.data_receiver = receiver



class FakeInputReceiver(_SpeccedMock):
    
    
    implements(IInputReceiver)

    faked_methods = [
        ('inputReceived', lambda *x: defer.succeed('done')),
    ]

    def inputReceived(self, data):
        pass




class FakeDataReceiver(_SpeccedMock):
    
    implements(IDataReceiver)

    faked_methods = [
        ('dataReceived', lambda *x: defer.succeed('done')),
    ]

    def dataReceived(self, data):
        pass



class FakeResultErrorReceiver(_SpeccedMock):
    
    implements(IResultErrorReceiver)

    faked_methods = [
        ('resultErrorReceived', lambda *x: defer.succeed('done')),
    ]
    

    def resultErrorReceived(self, error):
        pass

