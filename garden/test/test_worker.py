from twisted.trial.unittest import TestCase
from twisted.internet import defer
from zope.interface.verify import verifyClass, verifyObject

from garden.interface import IWorker
from garden.worker import BlockingWorker
from garden.test.fake import FakeResultSender



class BlockingWorkerTest(TestCase):


    def test_IWorker(self):
        verifyClass(IWorker, BlockingWorker)
        verifyObject(IWorker, BlockingWorker())


    def test_doWork(self):
        """
        The worker should be able to do work
        """
        w = BlockingWorker()
        w.sender = FakeResultSender()
        send_result = defer.Deferred()
        w.sender.sendResult.side_effect = lambda *a: send_result
        
        def foo(a, b):
            return a + b
        w.registerFunction('foo', 'version1', foo)
        
        r = w.doWork('bob', 'foo', 'version1', 'aaaa', [
            ('a', 'v1', 'xxxx', 'big', 'BIG'),
            ('b', 'v1', 'xxxx', 'fish', 'FISH'),
        ])
        self.assertFalse(r.called, "Should not be done, because the result "
                         "hasn't been sent, and BlockingWorker doesn't have "
                         "a queue of work to do.")
        w.sender.sendResult.assert_called_once_with('bob', 'foo', 'version1',
            'aaaa', 'bigfish', [
                ('a', 'v1', 'xxxx', 'BIG'),
                ('b', 'v1', 'xxxx', 'FISH'),
            ])
        send_result.callback('foo')
        self.assertTrue(r.called, "Now that the result is confirmed sent, "
                        "the work should be considered done")
