from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject


from garden.interface import IResultSender
from garden.test.fake import FakeResultSender



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
        f.sendError.assert_called_with('Yip', 'n', 'v', 'aaaa', 'error', [
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
        f.sendResult.assert_called_with('Yip', 'n', 'v', 'aaaa', 'value', [
            ('arg1', 'v1', 'bbbb', 'arg1hash'),
        ])