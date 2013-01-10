from hashlib import sha1

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



    def dispatchSinglePieceOfWork(self, entity, name, version, lineage,
                                  inputs, input_values):
        """
        XXX
        """
        hashes = [sha1(x).hexdigest() for x in input_values]
        return self.dispatcher(entity, name, version, lineage, inputs,
                               input_values, hashes)