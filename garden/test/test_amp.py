from twisted.trial.unittest import TestCase
from twisted.internet import defer, protocol
from zope.interface.verify import verifyClass, verifyObject

from twisted.test.proto_helpers import StringTransport

from mock import create_autospec


from garden.interface import (IWorkSource, IWorkReceiver, IResultSource,
                              IResultReceiver, IResultErrorReceiver,
                              IResultErrorSource)
from garden.amp import ReceiveWork, ReceiveResult, ReceiveError
from garden.amp import NoWorkerAvailable
from garden.amp import (GardenerFactory, GardenerProtocol, WorkerFactory,
                        WorkerProtocol)
from garden.util import RoundRobinChooser
from garden.test.fake import (FakeWorker, FakeWorkReceiver, FakeResultReceiver,
                              FakeResultErrorReceiver)



class GardenerFactoryTest(TestCase):


    def test_IWorkReceiver(self):
        verifyClass(IWorkReceiver, GardenerFactory)
        verifyObject(IWorkReceiver, GardenerFactory())


    def test_IResultSource(self):
        verifyClass(IResultSource, GardenerFactory)
        verifyObject(IResultSource, GardenerFactory())


    def test_IResultReceiver(self):
        verifyClass(IResultReceiver, GardenerFactory)
        verifyObject(IResultReceiver, GardenerFactory())


    def test_IResultErrorSource(self):
        verifyObject(IResultErrorSource, GardenerFactory())


    def test_IResultErrorReceiver(self):
        verifyObject(IResultErrorReceiver, GardenerFactory())


    def test_Factory(self):
        """
        Should use L{GardenerProtocol} by default and should be a factory
        """
        self.assertTrue(issubclass(GardenerFactory, protocol.Factory))
        self.assertEqual(GardenerFactory.protocol, GardenerProtocol)


    def test_buildProtocol(self):
        """
        Should set the Factory up as the result_receiver
        """
        f = GardenerFactory()
        p = f.buildProtocol('addr')
        self.assertEqual(p.factory, f)
        self.assertEqual(p.result_receiver, f, "Should set up the Factory "
                         "as the protocol's result_receiver")
        self.assertEqual(p.error_receiver, f, "Should add the error_receiver")


    def test_connectedProtocols(self):
        """
        Should keep track of the protocols that are connected.
        """
        f = GardenerFactory()
        ch = f.proto_chooser
        self.assertTrue(isinstance(ch, RoundRobinChooser))
        self.assertEqual(ch.options, [])
        
        ch.add = create_autospec(ch.add)
        ch.remove = create_autospec(ch.remove)
        
        # should know about connection
        p = f.buildProtocol('addr')
        transport = StringTransport()
        p.makeConnection(transport)
        ch.add.assert_called_once_with(p)
        
        # should know about disconnection
        transport.loseConnection()
        p.connectionLost(protocol.connectionDone)
        ch.remove.assert_called_once_with(p)


    def test_workReceived(self):
        """
        Should send work to the next protocol
        """
        f = GardenerFactory()
        
        d1 = defer.Deferred()
        
        p1 = FakeWorkReceiver()
        p1.workReceived.mock.side_effect = lambda *a: d1
        
        f.proto_chooser.add(p1)
        f.proto_chooser.next = create_autospec(f.proto_chooser.next,
                                return_value=p1)
        
        r = f.workReceived('Guy', 'bread', '1', 'aaaa', [])
        p1.workReceived.assert_called_once_with('Guy', 'bread', '1', 'aaaa', [])
        self.assertEqual(r, d1, "Should return the protocol's response")


    def test_workReceived_noprotocols(self):
        """
        If there are no protocols ready to take work, errback
        """
        f = GardenerFactory()
        r = f.workReceived('Foo', 'bread', '1', 'aaaa', [])
        self.assertFailure(r, NoWorkerAvailable)


    def test_setResultReceiver(self):
        """
        Should set the result_receiver
        """
        f = GardenerFactory()
        f.setResultReceiver('foo')
        self.assertEqual(f.result_receiver, 'foo')


    def test_resultReceived(self):
        """
        Received results should be sent to my result_receiver
        """
        f = GardenerFactory()
        f.setResultReceiver(FakeResultReceiver())
        r = f.resultReceived('joe', 'cake', '1', 'aaaa', 'val', [])
        f.result_receiver.resultReceived.assert_called_once_with('joe', 'cake',
            '1', 'aaaa', 'val', [])
        self.assertTrue(r.called)


    def test_resultErrorReceived(self):
        """
        Received errors should be sent to my result_receiver
        """
        f = GardenerFactory()
        receiver = FakeResultErrorReceiver()
        f.setResultErrorReceiver(receiver)
        r = f.resultErrorReceived('joe', 'cake', '1', 'aaaa', 'val', [])
        receiver.resultErrorReceived.assert_called_once_with('joe',
            'cake', '1', 'aaaa', 'val', [])
        self.assertTrue(r.called)



class GardenerProtocolTest(TestCase):


    def test_IWorkReceiver(self):
        verifyClass(IWorkReceiver, GardenerProtocol)
        verifyObject(IWorkReceiver, GardenerProtocol())


    def test_IResultSource(self):
        verifyClass(IResultSource, GardenerProtocol)
        verifyObject(IResultSource, GardenerProtocol())


    def test_IResultReceiver(self):
        verifyClass(IResultReceiver, GardenerProtocol)
        verifyObject(IResultReceiver, GardenerProtocol())


    def test_IResultErrorSource(self):
        verifyObject(IResultErrorSource, GardenerProtocol())


    def test_IResultErrorReceiver(self):
        verifyObject(IResultErrorReceiver, GardenerProtocol())


    def test_workReceived(self):
        """
        Will communicate the work over the wire.
        """
        p = GardenerProtocol()
        d = defer.Deferred()
        p.callRemote = create_autospec(p.callRemote, return_value=d)
        
        result = p.workReceived('Tumnus', 'spy', '2', 'vvvv', [
            ('snow', '1', 'cccc', 'val', 'hash'),
        ])
        p.callRemote.assert_called_once_with(ReceiveWork,
            entity='Tumnus',
            name='spy',
            version='2',
            lineage='vvvv',
            inputs=[
                ['snow', '1', 'cccc', 'val', 'hash']])
        self.assertFalse(result.called, "Other side hasn't acked yet")
        
        d.callback('foo')
        self.assertTrue(result.called, "Other side acked")


    def test_setResultReceiver(self):
        """
        By default, just set the result_receiver variable
        """
        p = GardenerProtocol()
        self.assertEqual(p.result_receiver, None)
        p.setResultReceiver('foo')
        self.assertEqual(p.result_receiver, 'foo')


    def test_resultReceived_resultErrorReceived(self):
        """
        By default, just pass the call along and transform the result to an
        empty dictionary.
        """
        p = GardenerProtocol()
        receiver = FakeResultReceiver()
        p.setResultReceiver(receiver)
        ereceiver = FakeResultErrorReceiver()
        p.setResultErrorReceiver(ereceiver)
        
        # resultReceived
        r = p.resultReceived('joe', 'cake', '1', 'vvvv', 'value', [])
        receiver.resultReceived.assert_called_once_with('joe', 'cake', '1',
                                                         'vvvv', 'value', [])
        self.assertEqual(self.successResultOf(r), {})

        # resultErrorReceived
        r = p.resultErrorReceived('joe', 'cake', '1', 'vvvv', 'error', [])
        ereceiver.resultErrorReceived.assert_called_once_with('joe', 'cake', '1',
                                                         'vvvv', 'error', [])
        self.assertEqual(self.successResultOf(r), {})



class WorkerFactoryTest(TestCase):


    def test_IResultReceiver(self):
        verifyClass(IResultReceiver, WorkerFactory)
        verifyObject(IResultReceiver, WorkerFactory())


    def test_IResultErrorReceiver(self):
        verifyObject(IResultErrorReceiver, WorkerFactory())


    def test_IWorkSource(self):
        verifyClass(IWorkSource, WorkerFactory)
        verifyObject(IWorkSource, WorkerFactory())


    def test_IWorkReceiver(self):
        verifyClass(IWorkReceiver, WorkerFactory)
        verifyObject(IWorkReceiver, WorkerFactory())


    def test_factory(self):
        self.assertTrue(issubclass(WorkerFactory, protocol.ClientFactory))
        self.assertEqual(WorkerFactory.protocol, WorkerProtocol)


    def test_setWorkReceiver(self):
        """
        Should set work_receiver is all
        """
        f = WorkerFactory()
        self.assertEqual(f.work_receiver, None)
        f.setWorkReceiver('foo')
        self.assertEqual(f.work_receiver, 'foo')


    def test_workReceived(self):
        """
        By default, just give the work to the work_receiver
        """
        f = WorkerFactory()
        receiver = FakeWorkReceiver()
        f.setWorkReceiver(receiver)
        
        result = f.workReceived('joe', 'cake', '1', 'aaaa', [])
        receiver.workReceived.assert_called_once_with('joe', 'cake', '1',
                                                      'aaaa', [])
        self.assertTrue(result.called, "Should call back")


    def test_resultReceived_resultErrorReceived(self):
        """
        In the normal case, should send the result over the single connected
        protocol.
        """
        f = WorkerFactory()
        p = FakeResultReceiver()
        f.connected_protocol = p
        
        # resultReceived
        p.resultReceived.mock.side_effect = lambda *a: defer.succeed('foo')
        result = f.resultReceived('entity', 'toast', '1', 'bbbb', 'value', [])
        p.resultReceived.assert_called_once_with('entity', 'toast', '1', 'bbbb',
                                                 'value', [])
        self.assertEqual(self.successResultOf(result), 'foo')
        
        # resultErrorReceived
        p = FakeResultErrorReceiver()
        f.connected_protocol = p
        p.resultErrorReceived.mock.side_effect = lambda *a: defer.succeed('bar')
        result = f.resultErrorReceived('entity', 'toast', '1', 'bbbb', 'value',
                                       [])
        p.resultErrorReceived.assert_called_once_with('entity', 'toast', '1',
                                                      'bbbb', 'value', [])
        self.assertEqual(self.successResultOf(result), 'bar')


    def test_connected_protocol(self):
        """
        The connected_protocol should only be set if there is a single,
        connected protocol ready to receive commands.
        """
        f = WorkerFactory()
        self.assertEqual(f.connected_protocol, None)
        
        p = f.buildProtocol('addr')
        self.assertEqual(p.work_receiver, f, "Should setWorkReceiver to the "
                         "factory")

        t = StringTransport()
        p.makeConnection(t)
        self.assertEqual(f.connected_protocol, p, "After protocol connects, "
                         "it should indicate to the Factory that he's the "
                         "connected protocol")
        
        t.loseConnection()
        p.connectionLost(protocol.connectionDone)
        self.assertEqual(f.connected_protocol, None, "When the protocol "
                         "disconnects, it should indicate to the Factory "
                         "that he's no longer available")



class WorkerProtocolTest(TestCase):


    def test_IResultReceiver(self):
        verifyClass(IResultReceiver, WorkerProtocol)
        verifyObject(IResultReceiver, WorkerProtocol())


    def test_IResultErrorReceiver(self):
        verifyObject(IResultErrorReceiver, WorkerProtocol())


    def test_IWorkSource(self):
        verifyClass(IWorkSource, WorkerProtocol)
        verifyObject(IWorkSource, WorkerProtocol())


    def test_IWorkReceiver(self):
        verifyClass(IWorkReceiver, WorkerProtocol)
        verifyObject(IWorkReceiver, WorkerProtocol())


    def test_setWorkReceiver(self):
        """
        Should just set work_receiver
        """
        p = WorkerProtocol()
        self.assertEqual(p.work_receiver, None)
        p.setWorkReceiver('foo')
        self.assertEqual(p.work_receiver, 'foo')


    def test_workReceived(self):
        """
        Should pass the work on to the work_receiver
        """
        p = WorkerProtocol()
        p.setWorkReceiver(FakeWorkReceiver())
        
        r = p.workReceived('joe', 'cake', '1', 'aaaa', [])
        p.work_receiver.workReceived.assert_called_once_with(
            'joe', 'cake', '1', 'aaaa', [])
        self.assertEqual(self.successResultOf(r), {})


    def test_resultReceived_resultErrorReceived(self):
        """
        Receiving a result should result in a remote call
        """
        p = WorkerProtocol()
        d = defer.succeed({})
        p.callRemote = create_autospec(p.callRemote, return_value=d)
        
        # resultReceived
        r = p.resultReceived('joe', 'cake', '1', 'aaaa', 'value', [])
        p.callRemote.assert_called_once_with(ReceiveResult,
            entity='joe',
            name='cake',
            version='1',
            lineage='aaaa',
            value='value',
            inputs=[])
        self.assertEqual(self.successResultOf(r), {})
        
        # resultErrorReceived
        p.callRemote.mock.reset_mock()
        p.callRemote.mock.return_value = defer.succeed({})
        r = p.resultErrorReceived('joe', 'cake', '1', 'aaaa', 'error', [])
        p.callRemote.assert_called_once_with(ReceiveError,
            entity='joe',
            name='cake',
            version='1',
            lineage='aaaa',
            error='error',
            inputs=[])
        self.assertEqual(self.successResultOf(r), {})



class FunctionalTest(TestCase):


    def test_work_send_receive(self):
        """
        GardenerFactory can send work to WorkerFactory's work_receiver
        """
        # gardener side of connection
        gfactory = GardenerFactory()
        gproto = gfactory.buildProtocol('foo')
        gproto.makeConnection(StringTransport())
        
        # worker side of connection
        wfactory = WorkerFactory()
        wproto = wfactory.buildProtocol('foo')
        wproto.makeConnection(StringTransport())
        
        # make a Worker
        worker = FakeWorker()
        wfactory.setWorkReceiver(worker)
        d = defer.Deferred()
        worker.workReceived.mock.side_effect = lambda *a: d
        
        # send some work
        r = gfactory.workReceived('Foo', 'cake', '1', 'aaaa', [
            ('wheat', '1', 'bbbb', 'foo', 'hash'),
        ])
        
        # communicate back and forth
        wproto.dataReceived(gproto.transport.value())
        gproto.dataReceived(wproto.transport.value())
        
        worker.workReceived.assert_called_once_with('Foo', 'cake', '1', 'aaaa', [
            ['wheat', '1', 'bbbb', 'foo', 'hash'],
        ])
        self.assertFalse(r.called, "Not done yet")

        gproto.transport.clear()
        wproto.transport.clear()
        d.callback('foo')
        
        wproto.dataReceived(gproto.transport.value())
        gproto.dataReceived(wproto.transport.value())
        self.assertTrue(r.called, "Done now")


    def test_result_send_receive(self):
        """
        WorkerFactory can send result to GardenerFactory's result_receiver
        """
        # gardener side of connection
        gfactory = GardenerFactory()
        gproto = gfactory.buildProtocol('foo')
        gproto.makeConnection(StringTransport())
        
        # worker side of connection
        wfactory = WorkerFactory()
        wproto = wfactory.buildProtocol('foo')
        wproto.makeConnection(StringTransport())
        
        # make a result Receiver
        receiver = FakeResultReceiver()
        gfactory.setResultReceiver(receiver)
        d = defer.Deferred()
        receiver.resultReceived.mock.side_effect = lambda *a: d
        
        # send some work
        r = wfactory.resultReceived('Foo', 'cake', '1', 'aaaa', 'value', [
            ('wheat', '1', 'bbbb', 'hash'),
        ])
        
        # communicate back and forth
        gproto.dataReceived(wproto.transport.value())
        wproto.dataReceived(gproto.transport.value())
        
        receiver.resultReceived.assert_called_once_with('Foo', 'cake', '1', 'aaaa', 'value', [
            ['wheat', '1', 'bbbb', 'hash'],
        ])
        self.assertFalse(r.called, "Not done yet")

        gproto.transport.clear()
        wproto.transport.clear()
        d.callback('foo')
        
        gproto.dataReceived(wproto.transport.value())
        wproto.dataReceived(gproto.transport.value())
        self.assertTrue(r.called, "Done now")


    def test_result_error_send_receive(self):
        """
        WorkerFactory can send errors to GardenerFactory's result_receiver
        """
        # gardener side of connection
        gfactory = GardenerFactory()
        gproto = gfactory.buildProtocol('foo')
        gproto.makeConnection(StringTransport())
        
        # worker side of connection
        wfactory = WorkerFactory()
        wproto = wfactory.buildProtocol('foo')
        wproto.makeConnection(StringTransport())
        
        # make a resultErrorReceiver
        receiver = FakeResultErrorReceiver()
        gfactory.setResultErrorReceiver(receiver)
        d = defer.Deferred()
        receiver.resultErrorReceived.mock.side_effect = lambda *a: d
        
        # send some work
        r = wfactory.resultErrorReceived('Foo', 'cake', '1', 'aaaa', 'value', [
            ('wheat', '1', 'bbbb', 'hash'),
        ])
        
        # communicate back and forth
        gproto.dataReceived(wproto.transport.value())
        wproto.dataReceived(gproto.transport.value())
        
        receiver.resultErrorReceived.assert_called_once_with('Foo', 'cake', '1', 'aaaa', 'value', [
            ['wheat', '1', 'bbbb', 'hash'],
        ])
        self.assertFalse(r.called, "Not done yet")

        gproto.transport.clear()
        wproto.transport.clear()
        d.callback('foo')
        
        gproto.dataReceived(wproto.transport.value())
        wproto.dataReceived(gproto.transport.value())
        self.assertTrue(r.called, "Done now")

