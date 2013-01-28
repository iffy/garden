"""
A collection of verified fakes for testing.
"""

__all__ = ['FakeReceiver']

from zope.interface import implements
from twisted.internet import defer

from mock import create_autospec

from garden.interface import IReceiver



class FakeReceiver(object):

    implements(IReceiver)

    def __init__(self, interfaces, return_factory=None):
        self.return_factory = return_factory or (lambda x: defer.succeed('ok'))
        self.receive = create_autospec(self.receive, side_effect=self._receive)
        self.results = []
        self.mapping = {}
        for i in interfaces:
            self.mapping[i] = self.receive


    def _receive(self, data):
        self.results.append(self.return_factory(data))
        return self.results[-1]


    def receiverMapping(self):
        return self.mapping


    def receive(self, what):
        pass


