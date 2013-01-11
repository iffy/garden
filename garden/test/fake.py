"""
A collection of verified fakes for testing.
"""

from zope.interface import implements
from twisted.internet import defer

from mock import create_autospec

from garden.interface import IResultSender



class SpeccedMock(object):

    methods = []

    def __init__(self):
        for method, ret in self.methods:
            setattr(self, method, create_autospec(getattr(self, method),
                    side_effect=ret))



class FakeResultSender(SpeccedMock):
    
    
    implements(IResultSender)
    
    
    methods = [
        ('sendError', lambda *x: defer.succeed('sent')),
        ('sendResult', lambda *x: defer.succeed('sent')),
    ]


    def sendError(self, entity, name, version, lineage, error, inputs):
        pass


    def sendResult(self, entity, name, version, lineage, value, inputs):
        pass