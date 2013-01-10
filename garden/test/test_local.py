from twisted.trial.unittest import TestCase


from garden.local import LocalWorkDispatcher, LocalWorker, InMemoryStore


class LocalWorkDispatcherTest(TestCase):


    def test_init(self):
        """
        You can give it a worker to use.
        """
        d = LocalWorkDispatcher('worker')
        self.assertEqual(d.worker, 'worker')



class LocalWorkerTest(TestCase):


    def test_addFunction(self):
        """
        You can add python functions to a worker
        """
        w = LocalWorker()
        def foo():
            pass
        w.addFunction('foo', 'v1', foo)



class InMemoryStoreTest(TestCase):


    def getInstance(self):
        return InMemoryStore()
