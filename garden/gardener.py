from twisted.internet import defer

from zope.interface import implements

from hashlib import sha1
from itertools import product

from garden.interface import (IGardener, IResultReceiver, IResultSource,
                              IDataSource, IDataReceiver, IWorkSource)
from garden.path import linealHash


def aggregateResult(deferred_list):
    """
    Aggregate a list of Deferreds into a single success or failure.  If any of
    the results fail, then the Deferred returned by this will errback.  If all
    of them succeed, this will callback with a list of the success results.
    """
    return defer.DeferredList(deferred_list, fireOnOneErrback=True, consumeErrors=True)




class InvalidResultFilter(object):
    """
    I discard results that were computed using inputs that are no longer valid
    or through a path that doesn't exist in the garden.
    """
    
    implements(IResultReceiver, IResultSource)
    
    result_receiver = None
    store = None
    garden = None
    
    
    def __init__(self, garden, store):
        self.store = store
        self.garden = garden


    def setResultReceiver(self, receiver):
        self.result_receiver = receiver


    def resultReceived(self, entity, name, version, lineage, value, inputs):
        """
        XXX
        """
        # check the garden
        valid_inputs = self.garden.inputsFor(name, version)
        # XXX magic numbers
        actual_inputs = [(x[0], x[1]) for x in inputs]
        if actual_inputs not in valid_inputs:
            return defer.succeed('invalid path')
        
        dlist = []
        
        for iname, iversion, ilineage, ihash in inputs:
            current_val = self.store.get(entity, iname, iversion, ilineage)
            current_val.addCallback(self._valueMatches, ihash)
            dlist.append(current_val)
        
        d = aggregateResult(dlist)
        d.addCallback(self._inputsMatch)
        d.addCallback(self._conditionallySend, entity, name, version, lineage,
                      value, inputs)
        return d


    def _valueMatches(self, current_val, ihash):
        """
        XXX
        """
        # XXX magic numbers
        return sha1(current_val[0][4]).hexdigest() == ihash


    def _inputsMatch(self, values):
        """
        XXX
        """
        matches = [x[1] for x in values]
        return False not in matches


    def _conditionallySend(self, do_send, entity, name, version, lineage, value,
                           inputs):
        """
        XXX
        """
        if do_send:
            return self.result_receiver.resultReceived(entity, name, version,
                                                       lineage, value, inputs)


    def resultErrorReceived(self, entity, name, version, lineage, error, inputs):
        return self.result_receiver.resultErrorReceived(entity, name, version,
                                                        lineage, error, inputs)



class DataStorer(object):
    """
    I store data to a L{IDataStore} before passing it on.  And I only pass it
    on if it has changed.
    """

    implements(IDataSource, IDataReceiver)


    def __init__(self, store):
        self.store = store


    def setDataReceiver(self, receiver):
        self.data_receiver = receiver


    def dataReceived(self, entity, name, version, lineage, value):
        """
        XXX
        """
        d = self.store.put(entity, name, version, lineage, value)
        d.addCallback(self._stored, entity, name, version, lineage, value)
        return d


    def _stored(self, result, entity, name, version, lineage, value):
        if not result['changed']:
            return
        return self.data_receiver.dataReceived(entity, name, version, lineage,
                                               value)



class WorkMaker(object):
    """
    I spawn work based on data received.
    """
    
    implements(IDataReceiver, IWorkSource)
    
    work_receiver = None

    
    def __init__(self, garden, store):
        self.garden = garden
        self.store = store


    def setWorkReceiver(self, receiver):
        self.work_receiver = receiver


    def dataReceived(self, entity, name, version, lineage, value):
        dlist = []
        
        for dst in self.garden.pathsRequiring(name, version):
            d = self.doPossibleWork(entity, *dst)
            dlist.append(d)
        return aggregateResult(dlist)


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
            value_list = aggregateResult(values)
            value_list.addCallback(self._gotValueList, entity, name, version)
            value_list.addCallback(lambda r:[x[1] for x in r])
            dlist.append(value_list)
        return aggregateResult(dlist)


    def _gotValueList(self, values, entity, name, version):
        values = [x[1] for x in values]
        dlist = []
        for combination in product(*values):
            lineages = [x[3] for x in combination]
            d = self.dispatchSinglePieceOfWork(entity, name, version,
                linealHash(name, version, lineages), list(combination))
            dlist.append(d)
        return aggregateResult(dlist)


    def dispatchSinglePieceOfWork(self, entity, name, version, lineage, values):
        # XXX magic numbers
        values = [x[1:] + (sha1(x[4]).hexdigest(),) for x in values]
        return self.work_receiver.workReceived(entity, name, version, lineage, values)




class Gardener(object):
    """
    I coordinate work based on new data.
    
    @ivar work_receiver: The L{IWorkReceiver} instance responsible for receiving
        the work I produce.
    
    @ivar data_receiver: The L{IDataReceiver} instance that will receive
        all new data.
    """
    
    implements(IGardener)
    
    
    work_receiver = None
    data_receiver = None
    
    
    def __init__(self, garden, store, accept_all_lineages=False):
        self.garden = garden
        self.store = store
        self.accept_all_lineages = accept_all_lineages


    def setWorkReceiver(self, receiver):
        """
        XXX
        """
        self.work_receiver = receiver


    def setDataReceiver(self, receiver):
        """
        XXX
        """
        self.data_receiver = receiver


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
        return self.dataReceived(entity, name, version, lineal_hash, value)


    def resultReceived(self, entity, name, version, lineage, value, inputs):
        """
        XXX
        """
        # check input hashes
        def gotValue(val, used_hash):
            # XXX magic numbers
            current_hash = sha1(val[0][4]).hexdigest()
            return current_hash == used_hash
        
        def checkMatches(result, entity, name, version, lineage, value):
            input_matches = [x[1] for x in result]
            if False in input_matches:
                # there were non-matching results
                return
            return self.dataReceived(entity, name, version, lineage, value)
            
        dlist = []
        # XXX we should also test that the given inputs are part of a valid
        # path in the Garden.
        for i in inputs:
            used_hash = i[3]
            r = self.store.get(entity, i[0], i[1], i[2])
            r.addCallback(gotValue, used_hash)
            dlist.append(r)
        
        r = aggregateResult(dlist)
        r.addCallback(checkMatches, entity, name, version, lineage, value)
        return r


    def resultErrorReceived(self, entity, name, version, lineage, error, inputs):
        """
        XXX I ignore things silently.  This ought not be.
        """
        return defer.succeed(True)


    def dataReceived(self, entity, name, version, lineage, value):
        """
        XXX
        """
        r = self.store.put(entity, name, version, lineage, value)
        return r.addCallback(self._dataStored, entity, name, version, lineage,
                             value)


    def _dataStored(self, result, entity, name, version, lineage, value):
        """
        XXX
        """
        if not result['changed']:
            # XXX this inaction should probably be logged
            return

        dlist = []
        if self.data_receiver:
            dlist.append(self.data_receiver.dataReceived(entity, name, version,
                                                         lineage, value))
        for dst in self.garden.pathsRequiring(name, version):
            d = self.doPossibleWork(entity, *dst)
            dlist.append(d)
        return aggregateResult(dlist)


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
            value_list = aggregateResult(values)
            value_list.addCallback(self._gotValueList, entity, name, version)
            value_list.addCallback(lambda r:[x[1] for x in r])
            dlist.append(value_list)
        return aggregateResult(dlist)


    def _gotValueList(self, values, entity, name, version):
        values = [x[1] for x in values]
        dlist = []
        for combination in product(*values):
            lineages = [x[3] for x in combination]
            d = self.dispatchSinglePieceOfWork(entity, name, version,
                linealHash(name, version, lineages), list(combination))
            dlist.append(d)
        return aggregateResult(dlist)


    def dispatchSinglePieceOfWork(self, entity, name, version, lineage, values):
        """
        XXX
        """
        values = [x[1:] + (sha1(x[4]).hexdigest(),) for x in values]
        return self.work_receiver.workReceived(entity, name, version, lineage,
                                         values)


