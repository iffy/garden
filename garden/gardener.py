from twisted.internet import defer
from hashlib import sha1
from itertools import product

from garden.path import linealHash



class Gardener(object):
    """
    I coordinate work based on new data.
    """
    
    
    def __init__(self, garden, store, dispatcher, accept_all_lineages=False):
        self.garden = garden
        self.store = store
        self.dispatcher = dispatcher
        self.accept_all_lineages = accept_all_lineages


    def inputReceived(self, entity, name, version, value):
        """
        New data, not from the result of a garden computation, received.
        
        @type entity: str
        @param entity: Entity to whom the data belongs.
        
        @type name: str
        @param name: Name of data
        
        @type version: str
        @param version: Version of data
        
        @type value: str
        @param value: Value of data
        """
        lineal_hash = linealHash(name, version)
        return self.dataReceived(entity, name, version, lineal_hash, 'value')


    def dataReceived(self, entity, name, version, lineage, value):
        """
        """


    def doPossibleWork(self, entity, name, version):
        """
        For the given C{entity}, compute the value of the given destination
        for all paths for which the inputs are in my C{store}.
        
        @type entity: str
        @param entity: Entity name
        
        @type name: str
        @param name: Destination name
        
        @type version: str
        @param version: Destination version
        
        @return: A C{Deferred} which will fire with a list of results of
            dispatching the work.
        """
        input_lists = self.garden.inputsFor(name, version)
        dlist = []
        for input_list in input_lists:
            values = [self.store.get(entity, x[0], x[1]) for x in input_list]
            value_list = defer.DeferredList(values)
            value_list.addCallback(self._gotValueList, entity, name, version)
            value_list.addCallback(lambda r:[x[1] for x in r])
            dlist.append(value_list)
        return defer.DeferredList(dlist).addCallback(self._flattenResult)


    def _gotValueList(self, values, entity, name, version):
        values = [x[1] for x in values]
        dlist = []
        for combination in product(*values):
            lineages = [x[3] for x in combination]
            d = self.dispatchSinglePieceOfWork(entity, name, version,
                linealHash(name, version, lineages), list(combination))
            dlist.append(d)
        return defer.DeferredList(dlist)


    def _flattenResult(self, result):
        ret = []
        map(ret.extend, [x[1] for x in result])
        return ret


    def dispatchSinglePieceOfWork(self, entity, name, version, lineage, values):
        """
        XXX
        """
        hashes = [sha1(x[4]).hexdigest() for x in values]
        return self.dispatcher(entity, name, version, lineage, values, hashes)