from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject


from garden.interface import (IResultReceiver, IWorkReceiver, IWorker, 
                              IGardener, IInputReceiver, IDataReceiver,
                              IResultErrorReceiver)
from garden.data import Input, Data, Work, Result, ResultError
from garden.test.fake import (FakeResultReceiver, FakeWorkReceiver, FakeWorker,
                              FakeGardener, FakeInputReceiver, FakeDataReceiver,
                              FakeResultErrorReceiver)



class FakeResultReceiverTest(TestCase):


    def test_IResultReceiver(self):
        verifyClass(IResultReceiver, FakeResultReceiver)
        verifyObject(IResultReceiver, FakeResultReceiver())


    def test_resultReceived(self):
        """
        By default, receives immediately
        """
        f = FakeResultReceiver()
        result = Result('Yip', 'n', 'v', 'aaaa', 'value', [
            ('arg1', 'v1', 'bbbb', 'arg1hash'),
        ])
        r = f.resultReceived(result)
        self.assertTrue(r.called, "Should call back immediately")
        f.resultReceived.assert_called_once_with(result)



class FakeResultErrorReceiverTest(TestCase):


    def test_IResultReceiver(self):
        verifyClass(IResultErrorReceiver, FakeResultErrorReceiver)
        verifyObject(IResultErrorReceiver, FakeResultErrorReceiver())


    def test_resultErrorReceived(self):
        """
        By default, succeeds immediately.
        """
        f = FakeResultErrorReceiver()
        error = ResultError('Yip', 'n', 'v', 'aaaa', 'error', [
            ('arg1', 'v1', 'bbbb', 'arg1hash'),
        ])
        r = f.resultErrorReceived(error)
        self.assertTrue(r.called, "Should call back immediately")
        f.resultErrorReceived.assert_called_once_with(error)



class FakeWorkReceiverTest(TestCase):


    def test_IWorkReceiver(self):
        verifyClass(IWorkReceiver, FakeWorkReceiver)
        verifyObject(IWorkReceiver, FakeWorkReceiver())


    def test_workReceived(self):
        """
        Should succeed immediately by default
        """
        f = FakeWorkReceiver()
        work = Work('Guy', 'name', 'v1', 'aaaa', [
            ('name', 'version', 'bbbb', 'val', 'hash'),
        ])
        r = f.workReceived(work)
        self.assertTrue(r.called, "Should call back immediately")
        f.workReceived.assert_called_once_with(work)



class FakeWorkerTest(TestCase):


    def test_IWorker(self):
        verifyClass(IWorker, FakeWorker)
        verifyObject(IWorker, FakeWorker())


    def test_workReceived(self):
        """
        Should succeed immediately by default
        """
        f = FakeWorker()
        work = Work('Guy', 'name', 'version', 'aaaa', [
            ('name', 'version', 'bbbb', 'val', 'hash'),
        ])
        r = f.workReceived(work)
        self.assertTrue(r.called, "Should call back immediately")
        f.workReceived.assert_called_once_with(work)


    def test_setResultReceiver(self):
        """
        Should set the result_receiver
        """
        f = FakeWorker()
        self.assertEqual(f.result_receiver, None)
        f.setResultReceiver('foo')
        self.assertEqual(f.result_receiver, 'foo')


    def test_setResultErrorReceiver(self):
        """
        Should be mocked
        """
        f = FakeWorker()
        f.setResultErrorReceiver('foo')
        f.setResultErrorReceiver.assert_called_once_with('foo')



class FakeGardenerTest(TestCase):


    def test_IGardener(self):
        verifyClass(IGardener, FakeGardener)
        verifyObject(IGardener, FakeGardener())


    def test_inputReceived(self):
        """
        By default, succeed immediately
        """
        f = FakeGardener()
        input = Input('Jim', 'name', 'version', 'value')
        r = f.inputReceived(input)
        self.assertTrue(r.called, "Should call back immediately")
        f.inputReceived.assert_called_once_with(input)


    def test_resultReceived(self):
        """
        Succeed immediately, by default.
        """
        f = FakeGardener()
        result = Result('Jim', 'name', 'version', 'aaaa', 'value', [
            ('name', 'version', 'bbbb', 'hash'),
        ])
        r = f.resultReceived(result)
        self.assertTrue(r.called, "Should call back immediately")
        f.resultReceived.assert_called_once_with(result)


    def test_resultErrorReceived(self):
        """
        Succeed immediately, by default.
        """
        f = FakeGardener()
        error = ResultError('Jim', 'name', 'version', 'aaaa', 'ERRR', [
            ('name', 'version', 'bbbb', 'hash'),
        ])
        r = f.resultErrorReceived(error)
        self.assertTrue(r.called, "Should call back immediately")
        f.resultErrorReceived.assert_called_once_with(error)


    def test_setWorkReceiver(self):
        """
        Should set the work_receiver
        """
        f = FakeGardener()
        self.assertEqual(f.work_receiver, None)
        f.setWorkReceiver('foo')
        self.assertEqual(f.work_receiver, 'foo')



class FakeInputReceiverTest(TestCase):
    
    
    def test_IInputReceiver(self):
        verifyClass(IInputReceiver, FakeInputReceiver)
        verifyObject(IInputReceiver, FakeInputReceiver())


    def test_inputReceived(self):
        """
        Succeed immediately by default
        """
        f = FakeInputReceiver()
        input = Input('Jim', 'name', 'version', 'value')
        r = f.inputReceived(input)
        self.assertTrue(r.called, "Should call back immediately")
        f.inputReceived.assert_called_once_with(input)


class FakeDataReceiverTest(TestCase):


    def test_IDataReceiver(self):
        verifyClass(IDataReceiver, FakeDataReceiver)
        verifyObject(IDataReceiver, FakeDataReceiver())


    def test_dataReceived(self):
        """
        Should succeed immediately by default
        """
        f = FakeDataReceiver()
        data = Data('Guy', 'name', 'v1', 'aaaa', 'value')
        r = f.dataReceived(data)
        self.assertTrue(r.called, "Should call back immediately")
        f.dataReceived.assert_called_once_with(data)


