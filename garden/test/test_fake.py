from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject


from garden.interface import (IResultReceiver, IWorkReceiver, IWorker, 
                              IGardener, IInputReceiver, IDataReceiver)
from garden.test.fake import (FakeResultReceiver, FakeWorkReceiver, FakeWorker,
                              FakeGardener, FakeInputReceiver, FakeDataReceiver)



class FakeResultReceiverTest(TestCase):


    def test_IResultReceiver(self):
        verifyClass(IResultReceiver, FakeResultReceiver)
        verifyObject(IResultReceiver, FakeResultReceiver())


    def test_resultErrorReceived(self):
        """
        By default, succeeds immediately.
        """
        f = FakeResultReceiver()
        r = f.resultErrorReceived('Yip', 'n', 'v', 'aaaa', 'error', [
            ('arg1', 'v1', 'bbbb', 'arg1hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.resultErrorReceived.assert_called_once_with('Yip', 'n', 'v', 'aaaa',
            'error', [
                ('arg1', 'v1', 'bbbb', 'arg1hash'),
            ])


    def test_resultReceived(self):
        """
        By default, receives immediately
        """
        f = FakeResultReceiver()
        r = f.resultReceived('Yip', 'n', 'v', 'aaaa', 'value', [
            ('arg1', 'v1', 'bbbb', 'arg1hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.resultReceived.assert_called_once_with('Yip', 'n', 'v', 'aaaa',
            'value', [
                ('arg1', 'v1', 'bbbb', 'arg1hash'),
            ])



class FakeWorkReceiverTest(TestCase):


    def test_IWorkReceiver(self):
        verifyClass(IWorkReceiver, FakeWorkReceiver)
        verifyObject(IWorkReceiver, FakeWorkReceiver())


    def test_workReceived(self):
        """
        Should succeed immediately by default
        """
        f = FakeWorkReceiver()
        r = f.workReceived('Guy', 'name', 'v1', 'aaaa', [
            ('name', 'version', 'bbbb', 'val', 'hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.workReceived.assert_called_once_with('Guy', 'name', 'v1', 'aaaa', [
            ('name', 'version', 'bbbb', 'val', 'hash'),
        ])



class FakeWorkerTest(TestCase):


    def test_IWorker(self):
        verifyClass(IWorker, FakeWorker)
        verifyObject(IWorker, FakeWorker())


    def test_workReceived(self):
        """
        Should succeed immediately by default
        """
        f = FakeWorker()
        r = f.workReceived('Guy', 'name', 'version', 'aaaa', [
            ('name', 'version', 'bbbb', 'val', 'hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.workReceived.assert_called_once_with('Guy', 'name', 'version',
            'aaaa', [
                ('name', 'version', 'bbbb', 'val', 'hash'),
            ])


    def test_setResultReceiver(self):
        """
        Should set the result_receiver
        """
        f = FakeWorker()
        self.assertEqual(f.result_receiver, None)
        f.setResultReceiver('foo')
        self.assertEqual(f.result_receiver, 'foo')




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


    def test_resultReceived(self):
        """
        Succeed immediately, by default.
        """
        f = FakeGardener()
        r = f.resultReceived('Jim', 'name', 'version', 'aaaa', 'value', [
            ('name', 'version', 'bbbb', 'hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.resultReceived.assert_called_once_with('Jim', 'name', 'version',
            'aaaa', 'value', [('name', 'version', 'bbbb', 'hash')])


    def test_resultErrorReceived(self):
        """
        Succeed immediately, by default.
        """
        f = FakeGardener()
        r = f.resultErrorReceived('Jim', 'name', 'version', 'aaaa', 'ERRR', [
            ('name', 'version', 'bbbb', 'hash'),
        ])
        self.assertTrue(r.called, "Should call back immediately")
        f.resultErrorReceived.assert_called_once_with('Jim', 'name', 'version',
            'aaaa', 'ERRR', [('name', 'version', 'bbbb', 'hash')])


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
        r = f.inputReceived('Jim', 'name', 'version', 'value')
        self.assertTrue(r.called, "Should call back immediately")
        f.inputReceived.assert_called_once_with('Jim', 'name', 'version',
                                                'value')


class FakeDataReceiverTest(TestCase):


    def test_IDataReceiver(self):
        verifyClass(IDataReceiver, FakeDataReceiver)
        verifyObject(IDataReceiver, FakeDataReceiver())


    def test_dataReceived(self):
        """
        Should succeed immediately by default
        """
        f = FakeDataReceiver()
        r = f.dataReceived('Guy', 'name', 'v1', 'aaaa', 'value')
        self.assertTrue(r.called, "Should call back immediately")
        f.dataReceived.assert_called_once_with('Guy', 'name', 'v1', 'aaaa', 'value')


