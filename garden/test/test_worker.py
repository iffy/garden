from twisted.trial.unittest import TestCase
from twisted.internet import defer
from zope.interface.verify import verifyClass, verifyObject

from garden.interface import ISource, IWorker, IWork, IResult, IResultError
from garden.data import Work
from garden.worker import BlockingWorker, ThreadedWorker
from garden.test.fake import FakeReceiver



class BlockingWorkerTest(TestCase):


    def test_IWorker(self):
        verifyClass(IWorker, BlockingWorker)
        verifyObject(IWorker, BlockingWorker())


    def test_sourceInterfaces(self):
        """
        Should be a source of results and errors
        """
        self.assertTrue(IResult in BlockingWorker.sourceInterfaces)
        self.assertTrue(IResultError in BlockingWorker.sourceInterfaces)


    def test_receiverMapping(self):
        """
        Should receive IWork, and that's it.
        """
        worker = BlockingWorker()
        mapping = worker.receiverMapping()
        self.assertEqual(mapping[IWork], worker.workReceived)


    def test_workReceived(self):
        """
        The worker should be able to receive work and do it.
        """
        receiver = FakeReceiver([IResult], lambda x: defer.Deferred())

        w = BlockingWorker()
        ISource(w).subscribe(receiver)
        
        def foo(a, b):
            return a + b
        w.registerFunction('foo', 'version1', foo)
        
        work = Work('bob', 'foo', 'version1', 'aaaa', [
            ('a', 'v1', 'xxxx', 'big', 'BIG'),
            ('b', 'v1', 'xxxx', 'fish', 'FISH'),
        ])
        r = w.workReceived(work)
        self.assertFalse(r.called, "Should not be done, because the result "
                         "hasn't been sent, and BlockingWorker doesn't have "
                         "a queue of work to do.")
        receiver.receive.assert_called_once_with(work.toResult('bigfish'))
        receiver.results[-1].callback('foo')
        self.assertTrue(r.called, "Now that the result is confirmed sent, "
                        "the work should be considered done")


    def test_workReceived_error(self):
        """
        If the work results in an Exception, send an error to the error receiver
        """
        receiver = FakeReceiver([IResultError], lambda x: defer.Deferred())
        
        w = BlockingWorker()
        ISource(w).subscribe(receiver)
        
        exc = Exception('something')
        def foo(a, b):
            raise exc
        w.registerFunction('foo', 'version1', foo)
        
        work = Work('bob', 'foo', 'version1', 'aaaa', [
            ('a', 'v1', 'xxxx', '', 'BIG'),
            ('b', 'v1', 'xxxx', '', 'FISH'),
        ])
        r = w.workReceived(work)
        self.assertFalse(r.called, "Should not be done because the error hasn't"
                         " yet been received by the receiver")
        receiver.receive.assert_called_once_with(work.toResultError(repr(exc)))
        receiver.results[-1].callback('foo')
        self.assertTrue(r.called, "Now that the error was received by the "
                        "receiver, we're good")


    def test_workReceived_list(self):
        """
        If the inputs are a list, that should be okay too
        """
        receiver = FakeReceiver([IResult])

        w = BlockingWorker()
        ISource(w).subscribe(receiver)
        
        def foo(a, b):
            return a + b
        w.registerFunction('foo', 'version1', foo)
        
        work = Work('bob', 'foo', 'version1', 'aaaa', [
            ['a', 'v1', 'xxxx', 'big', 'BIG'],
            ['b', 'v1', 'xxxx', 'fish', 'FISH'],
        ])
        r = w.workReceived(work)
        receiver.receive.assert_called_once_with(work.toResult('bigfish'))
        return r



class ThreadedWorkerTest(TestCase):


    def test_IWorker(self):
        verifyClass(IWorker, ThreadedWorker)
        verifyObject(IWorker, ThreadedWorker())


    def test_sourceInterfaces(self):
        """
        Should be a source of results and errors
        """
        self.assertTrue(IResult in ThreadedWorker.sourceInterfaces)
        self.assertTrue(IResultError in ThreadedWorker.sourceInterfaces)


    def test_receiverMapping(self):
        """
        Should receive IWork, and that's it.
        """
        worker = ThreadedWorker()
        mapping = worker.receiverMapping()
        self.assertEqual(mapping[IWork], worker.workReceived)


    @defer.inlineCallbacks
    def test_workReceived(self):
        """
        Should run the work in a thread
        """
        receiver = FakeReceiver([IResult])
        
        w = ThreadedWorker()
        ISource(w).subscribe(receiver)
        
        def foo(a, b):
            return a + b
        w.registerFunction('foo', 'version1', foo)
        
        work = Work('bob', 'foo', 'version1', 'aaaa', [
            ('a', 'v1', 'xxxx', 'big', 'BIG'),
            ('b', 'v1', 'xxxx', 'fish', 'FISH'),
        ])
        yield w.workReceived(work)
        receiver.receive.assert_called_once_with(work.toResult('bigfish'))


    @defer.inlineCallbacks
    def test_workReceived_error(self):
        """
        If there's an error doing the work, tell the result_receiver
        """
        receiver = FakeReceiver([IResultError])
        
        w = ThreadedWorker()
        ISource(w).subscribe(receiver)
        
        exc = Exception('foo')
        
        def foo(a):
            raise exc
        w.registerFunction('foo', 'v1', foo)
        
        work = Work('bob', 'foo', 'v1', 'xxxx', [
            ('a', 'v1', 'xxxx', 'big', 'BIG'),
        ])
        yield w.workReceived(work)
        receiver.receive.assert_called_once_with(work.toResultError(repr(exc)))


