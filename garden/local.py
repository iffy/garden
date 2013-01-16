from twisted.internet import defer
from zope.interface import implements


from garden.interface import IDataStore



class InMemoryStore(object):
    """
    I hold entity data in memory.
    """
    
    implements(IDataStore)


    def __init__(self):
        self._data = {}


    def _matchKey(self, key, entity, name=None, version=None, lineage=None):
        if key[0] != entity:
            return False
        if name is not None and key[1] != name:
            return False
        if version is not None and key[2] != version:
            return False
        if lineage is not None and key[3] != lineage:
            return False
        return True


    def get(self, entity, name=None, version=None, lineage=None):
        keys = [x for x in self._data if self._matchKey(x, entity, name, version, lineage)]
        return defer.succeed([k + (self._data[k],) for k in keys])


    def put(self, entity, name, version, lineage, value):
        old_value = self._data.get((entity, name, version, lineage), None)
        changed = value != old_value
        self._data[(entity, name, version, lineage)] = value
        return defer.succeed({'changed': changed})


