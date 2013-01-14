from twisted.internet import defer



class InMemoryStore(object):
    """
    I hold entity data in memory.
    """


    def __init__(self):
        self._data = {}


    def get(self, entity, name, version):
        keys = [x for x in self._data if x[:3] == (entity, name, version)]
        return defer.succeed([k + (self._data[k],) for k in keys])


    def put(self, entity, name, version, lineage, value):
        self._data[(entity, name, version, lineage)] = value
        return defer.succeed({'changed': True})


