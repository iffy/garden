from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath
from twisted.internet import defer
from zope.interface.verify import verifyObject


from garden.interface import IDataStore
from garden.store import SqliteStore



class IDataStoreTestMixin(object):


    def getInstance(self):
        raise NotImplementedError("To use the IDataStoreTestMixin, you must "
                                  "implement getInstance.  It should return "
                                  "an empty IDataStore instance")


    def test_IDataStore(self):
        verifyObject(IDataStore, self.getInstance())


    @defer.inlineCallbacks
    def test_IDataStore_get_empty(self):
        """
        Getting things that aren't there should result in empty lists.
        """
        store = self.getInstance()
        r = yield store.get('Sam', 'cake', '1', 'ffff')
        self.assertEqual(r, [])
        
        r = yield store.get('Sam', 'cake', '1')
        self.assertEqual(r, [])
        
        r = yield store.get('Sam', 'cake')
        self.assertEqual(r, [])
        
        r = yield store.get('Sam')
        self.assertEqual(r, [])


    @defer.inlineCallbacks
    def test_IDataStore_put(self):
        """
        You can put stuff in and get it out.
        """
        store = self.getInstance()
        r = yield store.put('Sam', 'cake', '1', 'ffff', 'value')
        self.assertEqual(r['changed'], True, "The store should report that"
                         " the value changed")
        
        r = yield store.put('Sam', 'cake', '1', 'ffff', 'value')
        self.assertEqual(r['changed'], False, "The store should report that the"
                         " value hasn't changed")
        
        r = yield store.put('Sam', 'cake', '1', 'ffff', 'hey')
        self.assertEqual(r['changed'], True, "The store should indicate that "
                         "the value has changed")
        
        r = yield store.get('Sam', 'cake', '1', 'ffff')
        self.assertEqual(r, [
            ('Sam', 'cake', '1', 'ffff', 'hey'),
        ])


    @defer.inlineCallbacks
    def test_IDataStore_get_many(self):
        """
        You can get all the data that matches broad or narrow queries.
        """
        store = self.getInstance()
        data = [
            ('Sam', 'cake', '1', 'ffff', 'value 1'),
            ('Sam', 'cake', '2', 'ffff', 'value 2'),
            ('Sam', 'cake', '3', 'bbbb', 'value 3'),
            ('Sam', 'flour', '1', 'ffff', 'value 4'),
            ('Sam', 'flour', '2', 'gggg', 'value 5'),
            ('Bob', 'cake', '1', 'aaaa', 'value 6'),
            ('Joe', 'apples', '2', 'bbbb', 'value 7'),
        ]
        for d in data:
            yield store.put(*d)
        
        # entity
        r = yield store.get('Sam')
        self.assertEqual(set(r), set([
            ('Sam', 'cake', '1', 'ffff', 'value 1'),
            ('Sam', 'cake', '2', 'ffff', 'value 2'),
            ('Sam', 'cake', '3', 'bbbb', 'value 3'),
            ('Sam', 'flour', '1', 'ffff', 'value 4'),
            ('Sam', 'flour', '2', 'gggg', 'value 5'),
        ]), "Should be able to select be entity only")
        
        # entity, name
        r = yield store.get('Sam', 'cake')
        self.assertEqual(set(r), set([
            ('Sam', 'cake', '1', 'ffff', 'value 1'),
            ('Sam', 'cake', '2', 'ffff', 'value 2'),
            ('Sam', 'cake', '3', 'bbbb', 'value 3'),
        ]), "Should be able to select on (entity, name)")

        # entity, version
        r = yield store.get('Sam', version='1')
        self.assertEqual(set(r), set([
            ('Sam', 'cake', '1', 'ffff', 'value 1'),
            ('Sam', 'flour', '1', 'ffff', 'value 4'),
        ]), "Should be able to select on (entity, version)")
        
        # entity, lineage
        r = yield store.get('Sam', lineage='bbbb')
        self.assertEqual(set(r), set([
            ('Sam', 'cake', '3', 'bbbb', 'value 3'),            
        ]), "Should be able to select on (entity, lineage)")

        # entity, name, version
        r = yield store.get('Sam', 'cake', '1')
        self.assertEqual(set(r), set([
            ('Sam', 'cake', '1', 'ffff', 'value 1'),
        ]), "Should be able to select on (entity, name, version)")
        
        # entity, name, lineage
        r = yield store.get('Sam', 'cake', lineage='ffff')
        self.assertEqual(set(r), set([
            ('Sam', 'cake', '1', 'ffff', 'value 1'),
            ('Sam', 'cake', '2', 'ffff', 'value 2'),
        ]), "Should be able to select on (entity, name, lineage)")
        
        # entity, version, lineage
        r = yield store.get('Sam', version='1', lineage='ffff')
        self.assertEqual(set(r), set([
            ('Sam', 'cake', '1', 'ffff', 'value 1'),
            ('Sam', 'flour', '1', 'ffff', 'value 4'),
        ]), "Should be able to select on (entity, version, lineage)")
        
        # entity, name, version, lineage
        r = yield store.get('Sam', 'cake', '3', 'bbbb')
        self.assertEqual(set(r), set([
            ('Sam', 'cake', '3', 'bbbb', 'value 3'),            
        ]), "Should be able to select on (entity, name, version, lineage)")




class SqliteStoreTest(TestCase, IDataStoreTestMixin):

    
    def getInstance(self):
        return SqliteStore(':memory:')


    @defer.inlineCallbacks
    def test_persist(self):
        """
        Should actually make a database file if you choose it on __init__
        """
        tmpfile = FilePath(self.mktemp())
        store = SqliteStore(tmpfile.path)
        
        yield store.put('Bob', 'eggs', '1', 'ffff', 'value')
        self.assertTrue(tmpfile.exists(), "Should have created the file: %r" % (
                        tmpfile.path,))
        
        store2 = SqliteStore(tmpfile.path)
        v = yield store2.get('Bob', 'eggs', '1', 'ffff')
        self.assertEqual(v, [
            ('Bob', 'eggs', '1', 'ffff', 'value'),
        ])
        



