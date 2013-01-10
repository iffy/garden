from twisted.trial.unittest import TestCase
from twisted.internet import defer

from mock import create_autospec
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


    def test_dataReceived_spawnWork(self):
        """
        If data is received that can cause work to happen, it should happen.
        """
        self.fail('Write me; I am functional')


    def test_dispatchSinglePieceOfWork(self):
        """
        You can dispatch a single function call to happen.
        """
        called = []
        ret = defer.Deferred()
        
        def dispatch(entity, name, version, lineage, inputs, input_values,
                     input_hashes):
            called.append((entity, name, version, lineage, inputs, input_values,
                           input_hashes))
            return ret
        
        g = Gardener(None, None, dispatch)
        r = g.dispatchSinglePieceOfWork('Bob', 'name', 'version', 'aaaa', [
            ('arg1', '1'),
            ('arg2', '1'),
        ], [
            'arg1 value',
            'arg2 value',
        ])
        
        self.assertEqual(called, [
            ('Bob', 'name', 'version', 'aaaa', [
                ('arg1', '1'),
                ('arg2', '1'),
            ], [
                'arg1 value',
                'arg2 value',
            ], [
                sha1('arg1 value').hexdigest(),
                sha1('arg2 value').hexdigest(),
            ]),
        ], "Should call dispatch function with all args, including SHA of "
           "input values")
        
        ret.callback('foo')
        self.assertEqual(self.successResultOf(r), 'foo')

    