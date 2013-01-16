from twisted.trial.unittest import TestCase

from garden.local import InMemoryStore
from garden.test.test_store import IDataStoreTestMixin



class InMemoryStore_IDataStoreTest(TestCase, IDataStoreTestMixin):


    def getInstance(self):
        return InMemoryStore()
       

