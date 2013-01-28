from twisted.trial.unittest import TestCase
from twisted.internet import defer
from zope.interface.verify import verifyClass, verifyObject

from garden.interface import IWorker, IWork, IResult, IResultError
from garden.data import Input, Data, Work, Result, ResultError
from garden.worker import BlockingWorker, ThreadedWorker
from garden.test.fake import FakeResultReceiver, FakeResultErrorReceiver



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
        receiver = FakeResultReceiver()
        receive_result = defer.Deferred()
        receiver.resultReceived.side_effect = lambda *a: receive_result

        w = BlockingWorker()        
        w.setResultReceiver(receiver)
        
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
        receiver.resultReceived.assert_called_once_with(work.toResult('bigfish'))
        receive_result.callback('foo')
        self.assertTrue(r.called, "Now that the result is confirmed sent, "
                        "the work should be considered done")


    def test_workReceived_error(self):
        """
        If the work results in an Exception, send an error to the error receiver
        """
        receiver = FakeResultErrorReceiver()
        result = defer.Deferred()
        receiver.resultErrorReceived.side_effect = lambda *a: result
        
        w = BlockingWorker()
        w.setResultErrorReceiver(receiver)
        
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
        receiver.resultErrorReceived.assert_called_once_with(
            work.toResultError(repr(exc)))
        result.callback('foo')
        self.assertTrue(r.called, "Now that the error was received by the "
                        "receiver, we're good")


    def test_workReceived_list(self):
        """
        If the inputs are a list, that should be okay too
        """
        receiver = FakeResultReceiver()

        w = BlockingWorker()        
        w.setResultReceiver(receiver)
        
        def foo(a, b):
            return a + b
        w.registerFunction('foo', 'version1', foo)
        
        work = Work('bob', 'foo', 'version1', 'aaaa', [
            ['a', 'v1', 'xxxx', 'big', 'BIG'],
            ['b', 'v1', 'xxxx', 'fish', 'FISH'],
        ])
        r = w.workReceived(work)
        receiver.resultReceived.assert_called_once_with(work.toResult('bigfish'))
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


    def test_setResultReceiver(self):
        """
        Should set result_receiver
        """
        t = ThreadedWorker()
        self.assertEqual(t.result_receiver, None)
        t.setResultReceiver('foo')
        self.assertEqual(t.result_receiver, 'foo')


    @defer.inlineCallbacks
    def test_workReceived(self):
        """
        Should run the work in a thread
        """
        receiver = FakeResultReceiver()
        
        w = ThreadedWorker()
        w.setResultReceiver(receiver)
        
        def foo(a, b):
            return a + b
        w.registerFunction('foo', 'version1', foo)
        
        work = Work('bob', 'foo', 'version1', 'aaaa', [
            ('a', 'v1', 'xxxx', 'big', 'BIG'),
            ('b', 'v1', 'xxxx', 'fish', 'FISH'),
        ])
        yield w.workReceived(work)
        receiver.resultReceived.assert_called_once_with(work.toResult('bigfish'))


    @defer.inlineCallbacks
    def test_workReceived_error(self):
        """
        If there's an error doing the work, tell the result_receiver
        """
        receiver = FakeResultErrorReceiver()
        receiver.resultErrorReceived.side_effect = lambda *a: defer.succeed('hey')
        
        w = ThreadedWorker()
        w.setResultErrorReceiver(receiver)
        
        exc = Exception('foo')
        
        def foo(a):
            raise exc
        w.registerFunction('foo', 'v1', foo)
        
        work = Work('bob', 'foo', 'v1', 'xxxx', [
            ('a', 'v1', 'xxxx', 'big', 'BIG'),
        ])
        r = yield w.workReceived(work)
        receiver.resultErrorReceived.assert_called_once_with(
            work.toResultError(repr(exc)))


