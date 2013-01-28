from twisted.internet import defer
from zope.interface import implements, providedBy

from collections import defaultdict

from garden.error import NothingToOffer
from garden.interface import ISource, IReceiver




class Source(object):
    
    
    implements(ISource)


    def __init__(self, interfaces=None):
        """
        @param interfaces: The set/list of interfaces that this source can
            provide.
        """
        self.interfaces = set(interfaces or [])
        self.receivers = defaultdict(lambda:[])


    def subscribe(self, receiver):
        """
        @raise NothingToOffer: If the receiver doesn't accept any of the
            interfaces I emit.
        """
        mapping = IReceiver(receiver).receiverMapping()
        expected = set(mapping)
        common = expected & self.interfaces
        if not common:
            raise NothingToOffer("This source only provides %r, not %r" % (
                                 list(self.interfaces), list(expected)))
        for interface in common:
            self.receivers[interface].append(mapping[interface])
        return list(common)


    def emit(self, data):
        """
        @raise TypeError: If the C{data} doesn't provide any of the interfaces
            I advertise to emit (from my initialization).
        """
        provided = providedBy(data)
        common = set(provided) & self.interfaces
        if not common:
            raise TypeError("%r does not implement any of my advertised "
                            "interfaces: %r" % (data, list(self.interfaces)))
        dlist = []
        for interface in provided:
            for func in self.receivers[interface]:
                dlist.append(defer.maybeDeferred(func, data))
        return defer.DeferredList(dlist, fireOnOneErrback=True, consumeErrors=True)