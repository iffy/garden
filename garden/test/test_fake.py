from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject


from garden.interface import IResultSender, IWorkSender, IWorker, IGardener
from garden.test.fake import (FakeResultSender, FakeWorkSender, FakeWorker,
                              FakeGardener)



class FakeResultSenderTest(TestCase):


    def test_IResultSender(self):
        verifyClass(IResultSender, FakeResultSender)
        verifyObject(IResultSender, FakeResultSender())


    def test_sendError(self):
        """
        By default, sending succeeds immediately.
        """
        f = FakeResultSender()
        r = f.sendError('Yip', 'n', 'v', 'aaaa', 'error', [
            ('arg1', 'v1', 'bbbb', 'arg1hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.sendError.assert_called_once_with('Yip', 'n', 'v', 'aaaa', 'error', [
            ('arg1', 'v1', 'bbbb', 'arg1hash'),
        ])


    def test_sendResult(self):
        """
        By default sending succeeds immediately.
        """
        f = FakeResultSender()
        r = f.sendResult('Yip', 'n', 'v', 'aaaa', 'value', [
            ('arg1', 'v1', 'bbbb', 'arg1hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.sendResult.assert_called_once_with('Yip', 'n', 'v', 'aaaa', 'value', [
            ('arg1', 'v1', 'bbbb', 'arg1hash'),
        ])



class FakeWorkSenderTest(TestCase):


    def test_IWorkSender(self):
        verifyClass(IWorkSender, FakeWorkSender)
        verifyObject(IWorkSender, FakeWorkSender())


    def test_sendWork(self):
        """
        Should succeed immediately by default
        """
        f = FakeWorkSender()
        r = f.sendWork('Guy', 'name', 'version', 'aaaa', [
            ('name', 'version', 'bbbb', 'val', 'hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.sendWork.assert_called_once_with('Guy', 'name', 'version', 'aaaa', [
            ('name', 'version', 'bbbb', 'val', 'hash'),
        ])



class FakeWorkerTest(TestCase):


    def test_IWorker(self):
        verifyClass(IWorker, FakeWorker)
        verifyObject(IWorker, FakeWorker())


    def test_doWork(self):
        """
        Should succeed immediately by default
        """
        f = FakeWorker()
        r = f.doWork('Guy', 'name', 'version', 'aaaa', [
            ('name', 'version', 'bbbb', 'val', 'hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.doWork.assert_called_once_with('Guy', 'name', 'version', 'aaaa', [
            ('name', 'version', 'bbbb', 'val', 'hash'),
        ])




class FakeGardenerTest(TestCase):


    def test_IGardener(self):
        verifyClass(IGardener, FakeGardener)
        verifyObject(IGardener, FakeGardener())


    def test_inputReceived(self):
        """
        By default, succeed immediately
        """
        f = FakeGardener()
        r = f.inputReceived('Jim', 'name', 'version', 'value')
        self.assertTrue(r.called, "Should call back immediately")
        f.inputReceived.assert_called_once_with('Jim', 'name', 'version',
                                                'value')


    def test_workReceived(self):
        """
        Succeed immediately, by default.
        """
        f = FakeGardener()
        r = f.workReceived('Jim', 'name', 'version', 'aaaa', 'value', [
            ('name', 'version', 'bbbb', 'hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.workReceived.assert_called_once_with('Jim', 'name', 'version', 'aaaa',
            'value', [('name', 'version', 'bbbb', 'hash')])
