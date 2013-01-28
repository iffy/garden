from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyObject
from twisted.internet import defer


from garden.interface import IReceiver, IInput
from garden.data import Input
from garden.glue import Source
from garden.test.fake import (FakeReceiver)



class FakeReceiverTest(TestCase):


    def test_IReceiver(self):
        verifyObject(IReceiver, FakeReceiver([]))


    def test_default(self):
        """
        You can use it to receive particular interfaces
        """
        source = Source([IInput])
        receiver = FakeReceiver([IInput])
        source.subscribe(receiver)
        
        data = Input('', '', '', '')
        r = source.emit(data)
        self.assertTrue(r.called, "Should callback immediately by default")
        receiver.receive.assert_called_once_with(data)
        self.assertEqual(len(receiver.results), 1)
        self.assertEqual(self.successResultOf(receiver.results[0]),
                         self.successResultOf(r)[0][1])


    def test_return_factory(self):
        """
        You can have a return_factory.
        """
        source = Source([IInput])
        receiver = FakeReceiver([IInput], lambda x: defer.Deferred())
        source.subscribe(receiver)
        
        data = Input('', '', '', '')
        r = source.emit(data)
        self.assertFalse(r.called, "Should not callback, because it's returning"
                         " Deferreds")
        self.assertEqual(len(receiver.results), 1)
        receiver.receive.assert_called_once_with(data)
        receiver.results[-1].callback('foo')
        self.assertTrue(r.called)

        



