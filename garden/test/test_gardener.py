from twisted.trial.unittest import TestCase
from twisted.internet import defer

from mock import create_autospec, Mock, call
from hashlib import sha1

from garden.local import InMemoryStore
from garden.path import Garden, linealHash
from garden.gardener import Gardener



class GardenerTest(TestCase):


    def test_init(self):
        """
        You can initialize with some things a Gardener needs.
        """
        g = Gardener('garden', 'store', 'dispatcher', accept_all_lineages=True)
        self.assertEqual(g.garden, 'garden')
        self.assertEqual(g.store, 'store')
        self.assertEqual(g.dispatcher, 'dispatcher')
        self.assertEqual(g.accept_all_lineages, True)


    def test_inputReceived(self):
        """
        When input is received, it should store the new data in the store
        and not return until dataReceived does.
        """
        g = Gardener(Garden(), 'store', 'dispatcher', accept_all_lineages=True)
        
        # fake out dataReceived, which is tested separately
        ret = defer.Deferred()
        g.dataReceived = create_autospec(g.dataReceived, return_value=ret)
        
        r = g.inputReceived('joe', 'name', 'version', 'value')
        g.dataReceived.assert_called_once_with('joe', 'name', 'version',
                                               linealHash('name', 'version'),
                                               'value')        
        ret.callback('foo')
        self.assertEqual(self.successResultOf(r), 'foo')


    def test_dataReceived(self):
        """
        Should store the data, then call doPossibleWork for all destinations
        for which the received data is an input.
        """
        store = InMemoryStore()
        store.put('Frog', 'eggs', '1', 'aaaa', 'eggs value')
        
        garden = Garden()
        garden.addPath('cake', '1', [
            ('eggs', '1'),
            ('flour', '1'),
        ])
        garden.addPath('german pancake', '1', [
            ('eggs', '1'),
            ('flour', '1'),
        ])
        
        g = Gardener(garden, store, None, accept_all_lineages=True)
        g.doPossibleWork = create_autospec(g.doPossibleWork,
                               side_effect=(lambda *x: defer.succeed(['hey'])))
        r = g.dataReceived('Frog', 'flour', '1', 'bbbb', 'flour value')
        
        v = store.get('Frog', 'flour', '1')
        self.assertEqual(self.successResultOf(v), [
            ('Frog', 'flour', '1', 'bbbb', 'flour value'),
        ], "Should have store the data in the store")
        
        g.doPossibleWork.assert_has_calls([
            call('Frog', 'cake', '1'),
            call('Frog', 'german pancake', '1'),
        ])
        self.assertEqual(self.successResultOf(r), ['hey', 'hey'])


    def test_dataReceived_waitForStorage(self):
        """
        doPossibleWork shouldn't be called until the data is stored.
        """
        store = InMemoryStore()
        d = defer.Deferred()
        store.put = create_autospec(store.put, return_value=d)
        
        garden = Garden()
        garden.addPath('cooked eggs', '1', [
            ('eggs', '1'),
        ])
        
        g = Gardener(garden, store, None, accept_all_lineages=True)
        g.doPossibleWork = create_autospec(g.doPossibleWork,
                               side_effect=(lambda *x: defer.succeed('hey')))
        r = g.dataReceived('Frog', 'eggs', '1', 'bbbb', 'flour value')
        
        self.assertEqual(g.doPossibleWork.call_count, 0, "Should not have "
                         "started doing work before the data is stored")
        d.callback({'changed': True})
        self.assertEqual(g.doPossibleWork.call_count, 1)


    def test_dispatchSinglePieceOfWork(self):
        """
        Dispatching a single function call through this function will result
        in the hashes being added to the function.
        """
        ret = defer.Deferred()
        dispatch = Mock(return_value=ret)
        
        g = Gardener(None, None, dispatch)
        r = g.dispatchSinglePieceOfWork('Bob', 'name', 'version', 'aaaa', [
            ('Bob', 'arg1', '1', 'aaaa', 'arg1 value'),
            ('Bob', 'arg2', '1', 'bbbb', 'arg2 value'),
        ])
        
        dispatch.assert_called_once_with('Bob', 'name', 'version', 'aaaa', [
                ('Bob', 'arg1', '1', 'aaaa', 'arg1 value'),
                ('Bob', 'arg2', '1', 'bbbb', 'arg2 value'),
            ], [
                sha1('arg1 value').hexdigest(),
                sha1('arg2 value').hexdigest(),
        ])
        
        ret.callback('foo')
        self.assertEqual(self.successResultOf(r), 'foo')


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
        
        def returner(*args):
            return defer.succeed('hello?')
        
        g = Gardener(garden, store, None, accept_all_lineages=True)
        g.dispatchSinglePieceOfWork = create_autospec(
            g.dispatchSinglePieceOfWork, side_effect=returner)
        
        return store, garden, g


    def test_doPossibleWork_nothing(self):
        """
        If there's no data, do no work.
        """
        store, garden, g = self.mkCakeSetup()
        
        r = g.doPossibleWork('sam', 'cake', '1')
        self.assertEqual([], self.successResultOf(r))


    def test_doPossibleWork_simple(self):
        """
        If there's enough data to do one piece of work, do that.
        """
        store, garden, g = self.mkCakeSetup()
        
        store.put('sam', 'eggs', '1', 'aaaa', 'eggs value')
        store.put('sam', 'flour', '1', 'bbbb', 'flour value')
                
        r = g.doPossibleWork('sam', 'cake', '1')
        g.dispatchSinglePieceOfWork.assert_called_once_with(
            'sam', 'cake', '1',
            linealHash('cake', '1', ['aaaa', 'bbbb']),
            [('sam', 'eggs', '1', 'aaaa', 'eggs value'),
             ('sam', 'flour', '1', 'bbbb', 'flour value')]
        )

        self.assertEqual(len(self.successResultOf(r)), 1)


    def test_doPossibleWork_multiLineage(self):
        """
        If there's data of multiple lineages, do work for both lineages.
        """
        store, garden, g = self.mkCakeSetup()

        store.put('sam', 'eggs', '1', 'aaaa', 'eggs value')
        store.put('sam', 'flour', '1', 'bbbb', 'flour value')
        store.put('sam', 'flour', '1', 'cccc', 'flour value 2')
        
        r = g.doPossibleWork('sam', 'cake', '1')
        g.dispatchSinglePieceOfWork.assert_has_calls([
            call('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'bbbb']),
                [('sam', 'eggs', '1', 'aaaa', 'eggs value'),
                 ('sam', 'flour', '1', 'bbbb', 'flour value')]),
            call('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'cccc']),
                [('sam', 'eggs', '1', 'aaaa', 'eggs value'),
                 ('sam', 'flour', '1', 'cccc', 'flour value 2')]),
        ])
        self.assertEqual(g.dispatchSinglePieceOfWork.call_count, 2)
        self.assertEqual(len(self.successResultOf(r)), 2)


    def test_doPossibleWork_multiPath(self):
        """
        If there's data for multiple paths, do work for all paths.
        """
        store, garden, g = self.mkCakeSetup()

        store.put('sam', 'eggs', '1', 'aaaa', 'eggs value')
        store.put('sam', 'flour', '1', 'bbbb', 'flour value')
        store.put('sam', 'flour', 'new', 'cccc', 'flour value 2')
        
        r = g.doPossibleWork('sam', 'cake', '1')
        g.dispatchSinglePieceOfWork.assert_has_calls([
            call('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'bbbb']),
                [('sam', 'eggs', '1', 'aaaa', 'eggs value'),
                 ('sam', 'flour', '1', 'bbbb', 'flour value')]),
            call('sam', 'cake', '1', linealHash('cake', '1', ['aaaa', 'cccc']),
                [('sam', 'eggs', '1', 'aaaa', 'eggs value'),
                 ('sam', 'flour', 'new', 'cccc', 'flour value 2')]),
        ])
        self.assertEqual(g.dispatchSinglePieceOfWork.call_count, 2)
        self.assertEqual(len(self.successResultOf(r)), 2)


