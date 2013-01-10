from twisted.trial.unittest import TestCase
from twisted.internet import defer

from mock import create_autospec, Mock

from garden.local import LocalWorkDispatcher, LocalWorker, InMemoryStore


class LocalWorkDispatcherTest(TestCase):


    def test_init(self):
        """
        You can give it a worker to use.
        """
        d = LocalWorkDispatcher('worker')
        self.assertEqual(d.worker, 'worker')


    def test_callable(self):
        """
        You can dispatch to the dispatcher, and results will end up in the
        result receiver
        """
        worker = LocalWorker()
        ret = defer.Deferred()
        worker.run = create_autospec(worker.run, return_value=ret)
        
        d = LocalWorkDispatcher(worker)
        receiver = Mock()
        d.sendResultsTo(receiver)
        r = d('entity', 'cake', '1', 'aaaa', [], ['hashes'])
        self.assertEqual(self.successResultOf(r), True, "Should immediately "
                         "fire with success, even though the worker isn't done")
        
        worker.run.assert_called_with('cake', '1', [])
        
        ret.callback('result')
        receiver.assert_called_once_with('entity', 'cake', '1', 'aaaa',
                                         'result', ['hashes'])



class LocalWorkerTest(TestCase):


    def test_addFunction(self):
        """
        You can add python functions to a worker
        """
        w = LocalWorker()
        def foo():
            pass
        w.addFunction('foo', 'v1', foo)


    def test_run(self):
        """
        You can run a function
        """
        w = LocalWorker()
        def foo(a):
            return 'something ' + a
        w.addFunction('foo', 'v1', foo)
        r = w.run('foo', 'v1', ['cool'])
        self.assertEqual(self.successResultOf(r), 'something cool')



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


