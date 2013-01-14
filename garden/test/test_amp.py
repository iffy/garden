from twisted.trial.unittest import TestCase
from twisted.internet import defer
from twisted.internet.protocol import Factory, connectionDone
from twisted.protocols import amp
from zope.interface.verify import verifyClass, verifyObject

from twisted.test.proto_helpers import StringTransport

from mock import create_autospec


from garden.interface import (IWorkSender, IWorkReceiver, IResultSender,
                              IResultReceiver)
from garden.amp import (WorkSender, WorkSenderProtocol, WorkReceiver,
                        ResultSender, DoWork, NoWorkerAvailable)
from garden.util import RoundRobinChooser
from garden.test.fake import FakeWorker, FakeWorkSender



class WorkSenderTest(TestCase):


    def test_IWorkSender(self):
        verifyClass(IWorkSender, WorkSender)
        verifyObject(IWorkSender, WorkSender())


    def test_Factory(self):
        """
        Should use L{WorkSenderProtocol} by default and should be a factory
        """
        self.assertTrue(issubclass(WorkSender, Factory))
        self.assertEqual(WorkSender.protocol, WorkSenderProtocol)


    def test_connectedProtocols(self):
        """
        Should keep track of the protocols that are connected.
        """
        f = WorkSender()
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
        r = transport.loseConnection()
        p.connectionLost(connectionDone)
        ch.remove.assert_called_once_with(p)


    def test_sendWork(self):
        """
        Should send work to the next protocol
        """
        f = WorkSender()
        
        d1 = defer.Deferred()
        
        p1 = FakeWorkSender()
        p1.sendWork.mock.side_effect = lambda *a: d1
        
        f.proto_chooser.add(p1)
        f.proto_chooser.next = create_autospec(f.proto_chooser.next,
                                return_value=p1)
        
        r = f.sendWork('Guy', 'bread', '1', 'aaaa', [])
        p1.sendWork.assert_called_once_with('Guy', 'bread', '1', 'aaaa', [])
        self.assertEqual(r, d1, "Should return the protocol's response")


    def test_sendWork_noprotocols(self):
        """
        If there are no protocols ready to take work, errback
        """
        f = WorkSender()
        r = f.sendWork('Foo', 'bread', '1', 'aaaa', [])
        self.assertFailure(r, NoWorkerAvailable)



class WorkSenderProtocolTest(TestCase):


    def test_IWorkSender(self):
        verifyClass(IWorkSender, WorkSenderProtocol)
        verifyObject(IWorkSender, WorkSenderProtocol())


    def test_sendWork(self):
        """
        Sending work should call DoWork on the remote side
        """
        sender = WorkSenderProtocol()
        
        ret = defer.Deferred()
        sender.callRemote = create_autospec(sender.callRemote, return_value=ret)
        
        r = sender.sendWork('Chef', 'cake', '1', 'aaaa', [
            ('eggs', '1', 'bbbb', 'foo', 'hash'),
            ('flour', '1', 'cccc', 'bar', 'hash2'),
        ])
        sender.callRemote.assert_called_once_with(DoWork,
            entity='Chef',
            name='cake',
            version='1',
            lineage='aaaa',
            inputs=[
                ['eggs', '1', 'bbbb', 'foo', 'hash'],
                ['flour', '1', 'cccc', 'bar', 'hash2'],
            ]
        )
        self.assertFalse(r.called, "Should not have called back yet")
        
        ret.callback('foo')
        self.assertTrue(r.called, "Other side acknowledged receipt")



class WorkReceiverTest(TestCase):


    def test_IWorkReceiver(self):
        verifyClass(IWorkReceiver, WorkReceiver)
        verifyObject(IWorkReceiver, WorkReceiver())


    def test_receiveWork(self):
        """
        Receiving work means making the worker do the work.
        """
        worker = FakeWorker()
        receiver = WorkReceiver()
        receiver.worker = worker
        
        d = defer.Deferred()
        worker.doWork.mock.side_effect = lambda *a: d
        
        r = receiver.receiveWork('Hal', 'door', '1', 'bbbb', [])
        self.assertFalse(r.called, "The work isn't done yet, and this protocol"
                         " has no queuing mechanism, so don't say you are done"
                         " with the data yet")
        
        d.callback('anything')
        self.assertEqual(self.successResultOf(r), {})



class FunctionalTest(TestCase):


    def test_work_send_receive(self):
        """
        WorkSender can send to WorkReceiver and cause work to happen.
        """
        sender_factory = WorkSender()
        
        sender = sender_factory.buildProtocol('foo')
        sender_transport = StringTransport()
        sender.makeConnection(sender_transport)
        
        receiver = WorkReceiver()
        receiver_transport = StringTransport()
        receiver.makeConnection(receiver_transport)
        
        worker = FakeWorker()
        receiver.worker = worker
        d = defer.Deferred()
        receiver.worker.doWork.mock.side_effect = lambda *a: d
        
        r = sender.callRemote(DoWork, entity='Foo',
            name='foo',
            version='foo',
            lineage='foo',
            inputs=[
                ['foo', 'bar', 'baz']])
        
        receiver.dataReceived(sender_transport.value())
        sender.dataReceived(receiver_transport.value())
        self.assertFalse(r.called, "Not done yet")

        sender_transport.clear()
        receiver_transport.clear()
        d.callback('foo')
        
        receiver.dataReceived(sender_transport.value())
        sender.dataReceived(receiver_transport.value())
        self.assertTrue(r.called, "Done now")



class ResultSenderTest(TestCase):


    def test_IResultSender(self):
        verifyClass(IResultSender, ResultSender)
        verifyObject(IResultSender, ResultSender())


    def test_sendError(self):
        """
        sendError should make a remote call
        """
        sender = ResultSender()
        
        ret = defer.Deferred()
        sender.callRemote = create_autospec(sender.callRemote, return_value=ret)
        
        r = sender.sendError('Chef', 'cake', '1', 'aaaa', 'error', [
            ('eggs', '1', 'bbbb', 'hash'),
            ('flour', '1', 'cccc', 'hash2'),
        ])
        sender.callRemote.assert_called_once_with(DoWork,
            entity='Chef',
            name='cake',
            version='1',
            lineage='aaaa',
            error='error',
            inputs=[
                ['eggs', '1', 'bbbb', 'foo', 'hash'],
                ['flour', '1', 'cccc', 'bar', 'hash2'],
            ]
        )
        self.assertFalse(r.called, "Should not have called back yet")
        
        ret.callback('foo')
        self.assertTrue(r.called, "Other side acknowledged receipt")

        

    
    
    
