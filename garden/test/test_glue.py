from twisted.trial.unittest import TestCase
from twisted.internet import defer
from zope.interface.verify import verifyObject
from zope.interface import Interface, implements

from mock import create_autospec

from garden.interface import ISource, IReceiver
from garden.glue import Source



class IA(Interface): pass
class A:
    implements(IA)

class IB(Interface): pass
class B:
    implements(IB)



class FakeReceiver:
    implements(IReceiver)


    def __init__(self, interfaces, return_value=None):
        self.received = []
        self.return_value = return_value
        self.mapping = {}
        for i in interfaces:
            self.mapping[i] = self.receive


    def receiverMapping(self):
        return self.mapping


    def receive(self, data):
        self.received.append(data)
        return self.return_value



class SourceTest(TestCase):


    def test_ISource(self):
        verifyObject(ISource, Source())


    def test_basic(self):
        """
        By default, you can subscribe to data of a particular type and receive
        emissions.
        """        
        source = Source()
        
        recv = FakeReceiver([IA, IB])
        source.subscribe(recv)
        
        a = A()
        b = B()
        source.emit(a)
        self.assertEqual(recv.received, [a])
        
        source.emit(b)
        self.assertEqual(recv.received, [a, b])


    def test_onlyReceivedRequestedInterfaces(self):
        """
        If a receiver doesn't accept a particular interface, it should not
        receive it.
        """
        source = Source()
        
        recv = FakeReceiver([IA])
        source.subscribe(recv)
        
        a = A()
        b = B()
        source.emit(a)
        self.assertEqual(recv.received, [a])
        
        source.emit(b)
        self.assertEqual(recv.received, [a], "Should not receive IB things")


    def test_emitReturn(self):
        """
        The emission should not return until all the receivers acknowledge
        receipt.
        """
        source = Source()
        
        recv1 = FakeReceiver([IA], defer.Deferred())
        source.subscribe(recv1)
        
        recv2 = FakeReceiver([IA], defer.Deferred())
        source.subscribe(recv2)
        
        a = A()
        r = source.emit(a)
        
        self.assertFalse(r.called, "Should not have called back yet")
        recv1.return_value.callback('foo')
        self.assertFalse(r.called)
        recv2.return_value.callback('foo')
        self.assertTrue(r.called)


    def test_emitError(self):
        """
        Errors should cause the result to errback
        """
        source = Source()
        
        recv1 = FakeReceiver([IA], defer.succeed('foo'))
        source.subscribe(recv1)
        
        recv2 = FakeReceiver([IA], defer.fail(Exception('foo')))
        source.subscribe(recv2)
        
        a = A()
        r = source.emit(a)
        def cb(r):
            self.fail("Should have errbacked")
        def eb(r):
            pass
        return r.addCallbacks(cb, eb)


