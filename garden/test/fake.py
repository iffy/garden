"""
A collection of verified fakes for testing.
"""

__all__ = ['FakeResultSender', 'FakeWorkSender']

from zope.interface import implements
from twisted.internet import defer

from mock import create_autospec

from garden.interface import IResultSender, IWorkSender



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