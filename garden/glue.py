from twisted.internet import defer
from zope.interface import implements, providedBy

from collections import defaultdict

from garden.interface import ISource, IReceiver




class Source(object):
    
    
    implements(ISource)


    def __init__(self):
        self.receivers = defaultdict(lambda:[])


    def subscribe(self, receiver):
        """
        XXX
        """
        for interface,func in IReceiver(receiver).receiverMapping().items():
            self.receivers[interface].append(func)


    def emit(self, data):
        """
        XXX
        """
        dlist = []
        for interface in providedBy(data):
            for func in self.receivers[interface]:
                dlist.append(defer.maybeDeferred(func, data))
        return defer.DeferredList(dlist, fireOnOneErrback=True, consumeErrors=True)