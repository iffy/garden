from twisted.trial.unittest import TestCase
from twisted.internet import defer

from zope.interface.verify import verifyClass, verifyObject

from mock import create_autospec, Mock

from garden.interface import (IWorkSender, IWorkReceiver, IResultSender,
                              IResultReceiver)
from garden.local import LocalDispatcher, InMemoryStore
from garden.test.fake import FakeWorker, FakeGardener



class LocalDispatcherTest(TestCase):


    def test_IWorkSender(self):
        verifyClass(IWorkSender, LocalDispatcher)
        verifyObject(IWorkSender, LocalDispatcher('foo'))


    def test_IWorkReceiver(self):
        verifyClass(IWorkReceiver, LocalDispatcher)
        verifyObject(IWorkReceiver, LocalDispatcher('foo'))


    def test_IResultSender(self):
        verifyClass(IResultSender, LocalDispatcher)
        verifyObject(IResultSender, LocalDispatcher('foo'))


    def test_IResultReceiver(self):
        verifyClass(IResultReceiver, LocalDispatcher)
        verifyObject(IResultReceiver, LocalDispatcher('foo'))


    def test_init(self):
        """
        You can give it a worker to use
        """
        worker = FakeWorker()
        d = LocalDispatcher(worker)
        self.assertEqual(d.worker, worker)
        self.assertEqual(d.gardener, None)


    def test_sendWork(self):
        """
        Giving L{LocalDispatcher} work will result in the worker being given
        the work.
        """
        worker = FakeWorker()
        ret = defer.Deferred()
        worker.doWork.mock.side_effect = lambda *x: ret

        d = LocalDispatcher(worker)
        r = d.sendWork('entity', 'cake', '1', 'aaaa', [
            ('arg', '1', 'bbbb', 'val', 'hash'),
        ])
        self.assertFalse(r.called, "Should not be done until the worker says "
                         "he got the value")
        ret.callback('result')
        self.assertEqual(self.successResultOf(r), 'result')


    def test_sendError(self):
        """
        Sending an error, will result in the Gardener getting the value
        """
        gardener = FakeGardener()
        d = LocalDispatcher(None)
        d.gardener = gardener
        
        ret = defer.Deferred()
        gardener.workErrorReceived.mock.side_effect = lambda *x: ret
        
        r = d.sendError('entity', 'cake', '1', 'aaaa', 'oven exploded', [])
        gardener.workErrorReceived.assert_called_once_with('entity', 'cake',
            '1', 'aaaa', 'oven exploded', [])
        self.assertFalse(r.called, "Should not be done until the other side "
                         "acknowledges receipt")

        ret.callback('foo')
        self.assertEqual(self.successResultOf(r), 'foo')


    def test_sendResult(self):
        """
        Sending a result, will result in the Gardener getting the value
        """
        gardener = FakeGardener()
        d = LocalDispatcher(None)
        d.gardener = gardener
        
        ret = defer.Deferred()
        gardener.workReceived.mock.side_effect = lambda *x: ret
        
        r = d.sendResult('entity', 'cake', '1', 'aaaa', 'delicious', [])
        gardener.workReceived.assert_called_once_with('entity', 'cake',
            '1', 'aaaa', 'delicious', [])
        self.assertFalse(r.called, "Should not be done until the other side "
                         "acknowledges receipt")

        ret.callback('foo')
        self.assertEqual(self.successResultOf(r), 'foo')



class InMemoryStoreTest(TestCase):


    def getInstance(self):
        return InMemoryStore()


    @defer.inlineCallbacks
    def test_get(self):
        """
        Should get values previously stored
        """
        store = self.getInstance()
        r = yield store.put('entity', 'name', 'version', 'lineage', 'value')
        self.assertEqual({'changed': True}, r)
        
        r = yield store.get('entity', 'name', 'version')
        self.assertEqual([
            ('entity', 'name', 'version', 'lineage', 'value'),
        ], r)


    @defer.inlineCallbacks
    def test_overwrite(self):
        """
        You can only have one value of the same entity, name, version and
        lineage.
        """
        store = self.getInstance()
        r = yield store.put('entity', 'name', 'version', 'lineage', 'value')
        r = yield store.put('entity', 'name', 'version', 'lineage', 'val2')
        r = yield store.get('entity', 'name', 'version')
        self.assertEqual([
            ('entity', 'name', 'version', 'lineage', 'val2'),
        ], r)
        

