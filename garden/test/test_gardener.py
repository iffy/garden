from twisted.trial.unittest import TestCase
from twisted.internet import defer

from zope.interface.verify import verifyClass, verifyObject

from mock import create_autospec, call
from hashlib import sha1

from garden.interface import (IGardener, IResultReceiver, IResultSource,
                              IDataSource, IDataReceiver, IWorkSource,
                              IData)
from garden.store import InMemoryStore
from garden.path import Garden
from garden.data import linealHash, Input, Data, Result, ResultError, Work
from garden.gardener import (Gardener, InvalidResultFilter, DataStorer,
                             WorkMaker)
from garden.test.fake import (FakeWorkReceiver, FakeDataReceiver,
                              FakeResultReceiver)



class GardenerTest(TestCase):


    def test_IGardener(self):
        verifyObject(IGardener, Gardener(None, None))


    def test_init(self):
        """
        You can initialize with some things a Gardener needs.
        """
        g = Gardener('garden', 'store')
        self.assertEqual(g.garden, 'garden')
        self.assertEqual(g.store, 'store')


    def test_setWorkReceiver(self):
        """
        Should just set work_receiver
        """
        g = Gardener(None, None)
        self.assertEqual(g.work_receiver, None)
        g.setWorkReceiver('foo')
        self.assertEqual(g.work_receiver, 'foo')




class InvalidResultFilterTest(TestCase):


    def test_IResultReceiver(self):
        verifyObject(IResultReceiver, InvalidResultFilter(None, None))
        verifyClass(IResultReceiver, InvalidResultFilter)


    def test_IResultSource(self):
        verifyObject(IResultSource, InvalidResultFilter(None, None))
        verifyClass(IResultSource, InvalidResultFilter)


    def test_setResultReceiver(self):
        """
        Should set the result_receiver
        """
        f = InvalidResultFilter(None, None)
        self.assertEqual(f.result_receiver, None)
        f.setResultReceiver('foo')
        self.assertEqual(f.result_receiver, 'foo')


    def test_resultReceived_hashcheck(self):
        """
        When a result is received, it is only accepted if the inputs on which
        it is based are still valid.
        """
        store = InMemoryStore()
        store.put(Data('joe', 'cake', '1', 'xxxx', 'chocolate'))
        
        garden = Garden()
        garden.addPath('happiness', '1', [
            ('cake', '1'),
        ])
        
        receiver = FakeResultReceiver()
        receiver.resultReceived.mock.side_effect = lambda *a: defer.succeed('a')
        
        f = InvalidResultFilter(garden, store)
        f.setResultReceiver(receiver)
        
        # receive a result not based on the correct input value
        r = f.resultReceived(Result('joe', 'happiness', '1', 'bbbb', 'yes', [
            ('cake', '1', 'xxxx', sha1('vanilla').hexdigest()),
        ]))
        self.assertEqual(receiver.resultReceived.call_count, 0, "Should not "
                         "have passed the result on")
        self.assertTrue(r.called)
        
        # receive a valid result (based on the current input value)
        result = Result('joe', 'happiness', '1', 'bbbb', 'yes', [
            ('cake', '1', 'xxxx', sha1('chocolate').hexdigest()),
        ])
        r = f.resultReceived(result)
        receiver.resultReceived.assert_called_once_with(result)
        self.assertEqual(self.successResultOf(r), 'a')


    def test_resultReceived_invalidPath(self):
        """
        If a result is received that was computed using arguments that don't
        correspond to a valid path in the garden, don't send the input on.
        """
        store = InMemoryStore()
        store.put(Data('joe', 'money', '1', 'xxxx', 'lots'))
        
        garden = Garden()
        garden.addPath('happiness', '1', [
            ('cake', '1'),
        ])
        
        receiver = FakeResultReceiver()
        
        f = InvalidResultFilter(garden, store)
        f.setResultReceiver(receiver)
        
        r = f.resultReceived(Result('joe', 'happiness', '1', 'bbbb', 'yes', [
            ('money', '1', 'xxxx', sha1('lots').hexdigest()),
        ]))
        self.assertEqual(receiver.resultReceived.call_count, 0, "Should not "
                         "send the result on, because money doesn't produce "
                         "happiness in this garden.  Only cake does that")
        self.assertTrue(r.called)


    def test_resultErrorReceived(self):
        """
        Should just be a pass-through
        """
        receiver = FakeResultReceiver()
        
        f = InvalidResultFilter(None, None)
        f.setResultReceiver(receiver)
        
        err = ResultError('joe', 'happiness', '1', 'bbbb', 'error', [])
        r = f.resultErrorReceived(err)
        receiver.resultErrorReceived.assert_called_once_with(err)
        self.assertTrue(r.called)



class DataStorerTest(TestCase):


    def test_IDataReceiver(self):
        verifyObject(IDataReceiver, DataStorer(None))


    def test_IDataSource(self):
        verifyObject(IDataSource, DataStorer(None))


    def test_dataReceived(self):
        """
        Should store the data, then pass it on, returning whatever the receiver
        returns.
        """
        store = InMemoryStore()
        store_d = defer.Deferred()
        store.put = create_autospec(store.put, return_value=store_d)
        
        fake = FakeDataReceiver()
        fake.dataReceived.mock.side_effect = lambda *a: defer.succeed('joe')
        
        s = DataStorer(store)
        s.setDataReceiver(fake)
        
        data = Data('sam', 'cake', '1', 'xxxx', 'value')
        result = s.dataReceived(data)
        self.assertEqual(fake.dataReceived.call_count, 0, "Should not have "
                         "passed the data on because it hasn't been stored yet")
        store.put.assert_called_once_with(data)
        self.assertFalse(result.called)
        store_d.callback({'changed': True})
        fake.dataReceived.assert_called_once_with(data)
        self.assertEqual(self.successResultOf(result), 'joe', "Should return "
                         "whatever the other receiver returns")


    def test_dataReceived_unchanged(self):
        """
        Don't pass data along if it's unchanged.
        """
        store = InMemoryStore()
        store.put(Data('ham', 'cake', '1', 'xxxx', 'value'))
        
        fake = FakeDataReceiver()
        
        s = DataStorer(store)
        s.setDataReceiver(fake)
        
        s.dataReceived(Data('ham', 'cake', '1', 'xxxx', 'value'))
        self.assertEqual(fake.dataReceived.call_count, 0, "Should not pass "
                         "along unchanged data")



class WorkMakerTest(TestCase):


    def test_IDataReceiver(self):
        verifyObject(IDataReceiver, WorkMaker(None, None))


    def test_IWorkSource(self):
        verifyObject(IWorkSource, WorkMaker(None, None))


    def test_dataReceived(self):
        """
        Should store the data, then call doPossibleWork for all destinations
        for which the received data is an input.
        """
        garden = Garden()
        garden.addPath('cake', '1', [
            ('eggs', '1'),
            ('flour', '1'),
        ])
        garden.addPath('german pancake', '1', [
            ('eggs', '1'),
            ('flour', '1'),
        ])
        
        w = WorkMaker(garden, None)
        w.doPossibleWork = create_autospec(w.doPossibleWork,
                               side_effect=(lambda *x: defer.succeed(['hey'])))
        r = w.dataReceived(Data('Frog', 'flour', '1', 'bbbb', 'flour value'))
        
        w.doPossibleWork.assert_has_calls([
            call('Frog', 'cake', '1'),
            call('Frog', 'german pancake', '1'),
        ])
        self.assertTrue(r.called)
        return r


    def mkCakeSetup(self):
        store = InMemoryStore()
        store = InMemoryStore()
        
        garden = Garden()
        garden.addPath('cake', '1', [
            ('eggs', '1'),
            ('flour', '1'),
        ])
        garden.addPath('cake', '1', [
            ('eggs', '1'),
            ('flour', 'new'),
        ])

        fake = FakeWorkReceiver()
        
        w = WorkMaker(garden, store)
        w.setWorkReceiver(fake)
        
        return store, garden, w, fake


    def test_doPossibleWork_nothing(self):
        """
        If there's no data, do no work.
        """
        store, garden, w, recv = self.mkCakeSetup()
        
        r = w.doPossibleWork('sam', 'cake', '1')
        self.assertTrue(r.called)
        return r


    def test_doPossibleWork_simple(self):
        """
        If there's enough data to do one piece of work, do that.
        """
        store, garden, w, recv = self.mkCakeSetup()
        
        store.put(Data('sam', 'eggs', '1', 'aaaa', 'eggs value'))
        store.put(Data('sam', 'flour', '1', 'bbbb', 'flour value'))
                
        r = w.doPossibleWork('sam', 'cake', '1')
        recv.workReceived.assert_called_once_with(Work('sam', 'cake', '1',
            linealHash('cake', '1', ['aaaa', 'bbbb']),
            [('eggs', '1', 'aaaa', 'eggs value'),
             ('flour', '1', 'bbbb', 'flour value')]
        ))

        self.assertTrue(r.called)
        return r


    def test_doPossibleWork_multiLineage(self):
        """
        If there's data of multiple lineages, do work for both lineages.
        """
        store, garden, w, recv = self.mkCakeSetup()

        store.put(Data('sam', 'eggs', '1', 'aaaa', 'eggs value'))
        store.put(Data('sam', 'flour', '1', 'bbbb', 'flour value'))
        store.put(Data('sam', 'flour', '1', 'cccc', 'flour value 2'))
        
        r = w.doPossibleWork('sam', 'cake', '1')
        recv.workReceived.assert_has_calls([
            call(Work('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'bbbb']),
                [('eggs', '1', 'aaaa', 'eggs value'),
                 ('flour', '1', 'bbbb', 'flour value')])),
            call(Work('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'cccc']),
                [('eggs', '1', 'aaaa', 'eggs value'),
                 ('flour', '1', 'cccc', 'flour value 2')])),
        ])
        self.assertEqual(recv.workReceived.call_count, 2)
        self.assertEqual(len(self.successResultOf(r)), 2)


    def test_doPossibleWork_multiPath(self):
        """
        If there's data for multiple paths, do work for all paths.
        """
        store, garden, w, recv = self.mkCakeSetup()

        store.put(Data('sam', 'eggs', '1', 'aaaa', 'eggs value'))
        store.put(Data('sam', 'flour', '1', 'bbbb', 'flour value'))
        store.put(Data('sam', 'flour', 'new', 'cccc', 'flour value 2'))
        
        r = w.doPossibleWork('sam', 'cake', '1')
        recv.workReceived.assert_has_calls([
            call(Work('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'bbbb']),
                [('eggs', '1', 'aaaa', 'eggs value'),
                 ('flour', '1', 'bbbb', 'flour value')])),
            call(Work('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'cccc']),
                [('eggs', '1', 'aaaa', 'eggs value'),
                 ('flour', 'new', 'cccc', 'flour value 2')])),
        ])
        self.assertEqual(recv.workReceived.call_count, 2)
        self.assertEqual(len(self.successResultOf(r)), 2)


    def test_dataReceived_errorReceiving(self):
        """
        If the work_receiver errsback on receiving any of the pieces of work,
        the whole dataReceived call should also errback.
        """
        store = InMemoryStore()
        store.put(Data('Jim', 'eggs', '1', 'xxxx', 'value'))
        
        garden = Garden()
        garden.addPath('cake', '1', [
            ('eggs', '1'),
        ])
        garden.addPath('cake', '2', [
            ('eggs', '1'),
        ])
        
        receiver = FakeWorkReceiver()
        receiver.workReceived.mock.side_effect = lambda *a: defer.fail(Exception('foo'))
        
        w = WorkMaker(garden, store)
        w.setWorkReceiver(receiver)
        
        r = w.dataReceived(Data('Jim', 'eggs', '1', 'xxxx', 'value'))
        self.assertFailure(r, Exception)


    def test_dataReceived_errorFetchingData(self):
        """
        If there's an error getting data for computing, the whole call should
        fail
        """
        store = InMemoryStore()
        store.get = create_autospec(store.get, side_effect=lambda *a: defer.fail(Exception('foo')))
        
        garden = Garden()
        garden.addPath('cake', '1', [
            ('eggs', '1'),
        ])
        
        w = WorkMaker(garden, store)
        
        r = w.dataReceived(Data('Jim', 'eggs', '1', 'xxxx', 'value'))
        self.assertFailure(r, Exception)
        return r.addErrback(lambda x:None)
                        


    
        


