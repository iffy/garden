from twisted.trial.unittest import TestCase
from twisted.internet import defer

from zope.interface.verify import verifyObject

from mock import create_autospec, call
from hashlib import sha1

from garden.interface import (IGardener, IReceiver, ISourceable, IWork, IData,
                              IInput, IResult, IResultError, ISource)
from garden.store import InMemoryStore
from garden.path import Garden
from garden.data import linealHash, Data, Result, Work
from garden.gardener import (Gardener, ToDataConverter,
                             InvalidResultFilter, DataStorer, WorkMaker)
from garden.test.fake import FakeReceiver



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



class ToDataConverterTest(TestCase):


    def test_IReceiver(self):
        """
        Should receive results
        """
        c = ToDataConverter()
        verifyObject(IReceiver, c)
        
        mapping = c.receiverMapping()
        self.assertEqual(mapping[IResult], c.dataReceived)
        self.assertEqual(mapping[IResultError], c.resultErrorReceived)
        self.assertEqual(mapping[IInput], c.dataReceived)


    def test_ISourceable(self):
        """
        Should be a source of Data
        """
        c = ToDataConverter()
        verifyObject(ISourceable, c)
        
        self.assertIn(IData, c.sourceInterfaces)


    def test_resultReceived(self):
        """
        Should emit Data
        """        
        c = ToDataConverter()
        
        recv = FakeReceiver([IData], lambda x: defer.Deferred())
        ISource(c).subscribe(recv)
        
        result = Result('joe', 'cake', '1', 'xxxx', 'value', [])
        r = c.dataReceived(result)
        self.assertFalse(r.called, "Should not callback yet")
        
        recv.receive.assert_called_once_with(IData(result))
        recv.results[-1].callback('foo')
        self.assertTrue(r.called)
        




class InvalidResultFilterTest(TestCase):


    def test_IReceiver(self):
        verifyObject(IReceiver, InvalidResultFilter(None, None))

        f = InvalidResultFilter(None, None)
        mapping = f.receiverMapping()
        self.assertEqual(mapping[IResult], f.resultReceived)
        self.assertEqual(mapping[IResultError], f.resultReceived)


    def test_ISourceable(self):
        verifyObject(ISourceable, InvalidResultFilter(None, None))
        self.assertTrue(IResult in InvalidResultFilter.sourceInterfaces)
        self.assertTrue(IResultError in InvalidResultFilter.sourceInterfaces)


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
        
        receiver = FakeReceiver([IResult])
        
        f = InvalidResultFilter(garden, store)
        ISource(f).subscribe(receiver)
        
        # receive a result not based on the correct input value
        r = f.resultReceived(Result('joe', 'happiness', '1', 'bbbb', 'yes', [
            ('cake', '1', 'xxxx', sha1('vanilla').hexdigest()),
        ]))
        self.assertEqual(receiver.receive.call_count, 0, "Should not "
                         "have passed the result on")
        self.assertTrue(r.called)
        
        # receive a valid result (based on the current input value)
        result = Result('joe', 'happiness', '1', 'bbbb', 'yes', [
            ('cake', '1', 'xxxx', sha1('chocolate').hexdigest()),
        ])
        r = f.resultReceived(result)
        receiver.receive.assert_called_once_with(result)
        self.assertTrue(self.successResultOf(r))


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
        
        receiver = FakeReceiver([IResult])
        
        f = InvalidResultFilter(garden, store)
        ISource(f).subscribe(receiver)
        
        r = f.resultReceived(Result('joe', 'happiness', '1', 'bbbb', 'yes', [
            ('money', '1', 'xxxx', sha1('lots').hexdigest()),
        ]))
        self.assertEqual(receiver.receive.call_count, 0, "Should not "
                         "send the result on, because money doesn't produce "
                         "happiness in this garden.  Only cake does that")
        self.assertTrue(r.called)



class DataStorerTest(TestCase):


    def test_IReceiver(self):
        verifyObject(IReceiver, DataStorer(None))
        
        s = DataStorer(None)
        mapping = s.receiverMapping()
        self.assertEqual(mapping[IData], s.dataReceived)


    def test_ISourceable(self):
        verifyObject(ISourceable, DataStorer(None))
        
        self.assertTrue(IData in DataStorer.sourceInterfaces)


    def test_dataReceived(self):
        """
        Should store the data, then pass it on, returning whatever the receiver
        returns.
        """
        store = InMemoryStore()
        store_d = defer.Deferred()
        store.put = create_autospec(store.put, return_value=store_d)
        
        fake = FakeReceiver([IData])
        
        s = DataStorer(store)
        ISource(s).subscribe(fake)
        
        data = Data('sam', 'cake', '1', 'xxxx', 'value')
        result = s.dataReceived(data)
        self.assertEqual(fake.receive.call_count, 0, "Should not have "
                         "passed the data on because it hasn't been stored yet")
        store.put.assert_called_once_with(data)
        self.assertFalse(result.called)
        store_d.callback({'changed': True})
        fake.receive.assert_called_once_with(data)
        self.assertTrue(self.successResultOf(result), "Should return "
                         "whatever the other receiver returns")


    def test_dataReceived_unchanged(self):
        """
        Don't pass data along if it's unchanged.
        """
        store = InMemoryStore()
        store.put(Data('ham', 'cake', '1', 'xxxx', 'value'))
        
        fake = FakeReceiver([IData])
        
        s = DataStorer(store)
        ISource(s).subscribe(fake)
        
        s.dataReceived(Data('ham', 'cake', '1', 'xxxx', 'value'))
        self.assertEqual(fake.receive.call_count, 0, "Should not pass "
                         "along unchanged data")



class WorkMakerTest(TestCase):


    def test_IReceiver(self):
        verifyObject(IReceiver, WorkMaker(None, None))
        
        maker = WorkMaker(None, None)
        mapping = maker.receiverMapping()
        self.assertEqual(mapping[IData], maker.dataReceived)


    def test_ISourceable(self):
        verifyObject(ISourceable, WorkMaker(None, None))
        
        self.assertTrue(IWork in WorkMaker.sourceInterfaces)


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

        receiver = FakeReceiver([IWork])
        
        w = WorkMaker(garden, store)
        ISource(w).subscribe(receiver)
        
        return store, garden, w, receiver


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
        recv.receive.assert_called_once_with(Work('sam', 'cake', '1',
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
        recv.receive.assert_has_calls([
            call(Work('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'bbbb']),
                [('eggs', '1', 'aaaa', 'eggs value'),
                 ('flour', '1', 'bbbb', 'flour value')])),
            call(Work('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'cccc']),
                [('eggs', '1', 'aaaa', 'eggs value'),
                 ('flour', '1', 'cccc', 'flour value 2')])),
        ])
        self.assertEqual(recv.receive.call_count, 2)
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
        recv.receive.assert_has_calls([
            call(Work('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'bbbb']),
                [('eggs', '1', 'aaaa', 'eggs value'),
                 ('flour', '1', 'bbbb', 'flour value')])),
            call(Work('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'cccc']),
                [('eggs', '1', 'aaaa', 'eggs value'),
                 ('flour', 'new', 'cccc', 'flour value 2')])),
        ])
        self.assertEqual(recv.receive.call_count, 2)
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
        
        receiver = FakeReceiver([IWork], lambda x: defer.fail(Exception('foo')))
        
        w = WorkMaker(garden, store)
        ISource(w).subscribe(receiver)
        
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
                        


    
        


