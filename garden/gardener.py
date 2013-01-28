from twisted.internet import defer

from zope.interface import implements

from hashlib import sha1
from itertools import product

from garden.interface import (IGardener, IWorkInput, IWork, IData, ISource,
                              ISourceable, IResult, IResultError, IReceiver)
from garden.data import linealHash, Work


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
    
    implements(ISourceable, IReceiver)
    sourceInterfaces = [IResult, IResultError]
    
    store = None
    garden = None
    
    
    def __init__(self, garden, store):
        self.store = store
        self.garden = garden


    def receiverMapping(self):
        return {
            IResult: self.resultReceived,
            IResultError: self.resultReceived,
        }


    def resultReceived(self, result):
        """
        XXX
        """
        # check the garden
        valid_inputs = self.garden.inputsFor(result.name, result.version)
        # XXX magic numbers
        actual_inputs = [(x.name, x.version) for x in result.inputs]
        if actual_inputs not in valid_inputs:
            return defer.succeed('invalid path')
        
        dlist = []
        
        for i in result.inputs:
            current_val = self.store.get(result.entity, i.name, i.version,
                                         i.lineage)
            current_val.addCallback(self._valueMatches, i.hash)
            dlist.append(current_val)
        
        d = aggregateResult(dlist)
        d.addCallback(self._inputsMatch)
        d.addCallback(self._conditionallySend, result)
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


    def _conditionallySend(self, do_send, result):
        """
        XXX
        """
        if do_send:
            return ISource(self).emit(result)



class DataStorer(object):
    """
    I store data to a L{IDataStore} before passing it on.  And I only pass it
    on if it has changed.
    """

    implements(ISourceable, IReceiver)
    sourceInterfaces = (IData,)


    def __init__(self, store):
        self.store = store


    def receiverMapping(self):
        return {
            IData: self.dataReceived,
        }


    def dataReceived(self, data):
        """
        XXX
        """
        d = self.store.put(data)
        d.addCallback(self._stored, data)
        return d


    def _stored(self, result, data):
        if not result['changed']:
            return
        return ISource(self).emit(data)



class WorkMaker(object):
    """
    I spawn work based on data received and paths in the Garden.
    """
    
    implements(ISourceable, IReceiver)
    sourceInterfaces = (IWork,)


    def __init__(self, garden, store):
        self.garden = garden
        self.store = store


    def receiverMapping(self):
        return {
            IData: self.dataReceived,
        }


    def dataReceived(self, data):
        dlist = []
        
        for dst in self.garden.pathsRequiring(data.name, data.version):
            d = self.doPossibleWork(data.entity, *dst)
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
            lineages = [x.lineage for x in combination]
            work = Work(entity, name, version,
                        linealHash(name, version, lineages),
                        [IWorkInput(x) for x in combination])
            d = ISource(self).emit(work)
            dlist.append(d)
        return aggregateResult(dlist)



class Gardener(object):
    """
    I coordinate work based on new data.
    
    I am currently not test driven, except for the functional test that is the
    README :(
    
    @ivar work_receiver: The L{IWorkReceiver} instance responsible for receiving
        the work I produce.
    
    @ivar data_receiver: The L{IDataReceiver} instance that will receive
        all new data.
    """
    
    implements(IGardener)
    
    
    work_receiver = None
    data_receiver = None
    
    
    def __init__(self, garden, store):
        self.garden = garden
        self.store = store
        self.result_filter = InvalidResultFilter(garden, store)
        self.storer = DataStorer(store)
        self.work_maker = WorkMaker(garden, store)
        self.storer.setDataReceiver(self.work_maker)


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


    def inputReceived(self, data):
        """
        New data, not from the result of a garden computation, received.

        XXX I am not tested.
        """
        return self.dataReceived(IData(data))


    def resultReceived(self, result):
        """
        XXX
        """
        return self.result_filter.resultReceived(result)


    def resultErrorReceived(self, error):
        """
        XXX I ignore things silently.  This ought not be.
        """
        return defer.succeed(True)


    def dataReceived(self, data):
        """
        XXX
        """
        return self.storer.dataReceived(data)
        


    def doPossibleWork(self, entity, name, version):
        """
        XXX
        """


