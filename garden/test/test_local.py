from twisted.trial.unittest import TestCase
from twisted.internet import defer

from garden.local import InMemoryStore



class InMemoryStoreTest(TestCase):


    def getInstance(self):
        return InMemoryStore()


    @defer.inlineCallbacks
    def test_get(self):
        """
        Should get values previously stored
        """
        store = self.getInstance()
        r = yield store.put('entity', 'name', 'version', 'lineage', 'value')
        self.assertEqual({'changed': True}, r)
        
        r = yield store.get('entity', 'name', 'version')
        self.assertEqual([
            ('entity', 'name', 'version', 'lineage', 'value'),
        ], r)


    @defer.inlineCallbacks
    def test_overwrite(self):
        """
        You can only have one value of the same entity, name, version and
        lineage.
        """
        store = self.getInstance()
        r = yield store.put('entity', 'name', 'version', 'lineage', 'value')
        r = yield store.put('entity', 'name', 'version', 'lineage', 'val2')
        r = yield store.get('entity', 'name', 'version')
        self.assertEqual([
            ('entity', 'name', 'version', 'lineage', 'val2'),
        ], r)
        

