from zope.interface import Interface, Attribute
from twisted.python import components



class IInput(Interface):

    entity = Attribute("Entity name")
    name = Attribute("Data name")
    version = Attribute("Data version")
    value = Attribute("Data value")



class IData(Interface):

    entity = Attribute("Entity name")
    name = Attribute("Data name")
    version = Attribute("Data version")
    lineage = Attribute("Data lineage")
    value = Attribute("Data value")



class IWork(Interface):

    entity = Attribute("Entity name")
    name = Attribute("Destination name")
    version = Attribute("Destination version")
    lineage = Attribute("Destination lineage")
    inputs = Attribute("List of IWorkInputs")



class IWorkInput(Interface):

    name = Attribute("Data name")
    version = Attribute("Data version")
    lineage = Attribute("Data lineage")
    value = Attribute("Data value")
    hash = Attribute("Value hash")



class IResult(Interface):

    entity = Attribute("Entity name")
    name = Attribute("Data name")
    version = Attribute("Data version")
    lineage = Attribute("Data lineage")
    value = Attribute("Data value")
    inputs = Attribute("List of IResultInputs")



class IResultInput(Interface):

    name = Attribute("Data name")
    version = Attribute("Data version")
    lineage = Attribute("Data lineage")
    hash = Attribute("Value hash")



class IResultError(Interface):

    entity = Attribute("Entity name")
    name = Attribute("Data name")
    version = Attribute("Data version")
    lineage = Attribute("Data lineage")
    error = Attribute("Error string")
    inputs = Attribute("List of IResultInputs")



class ISource(Interface):


    def subscribe(receiver):
        """
        Add an IReceiver to be called with data of a particular interface.
        
        @type receiver: L{IReceiver}
        
        @raise NothingToOffer: If the receiver can't accept any of the data
            this source can provide.
        """


    def emit(data):
        """
        Emit some data to all this source's subscribers.
        
        @return: A C{DeferredList}
        """



class ISourceable(Interface):


    sourceInterfaces = Attribute("A list of the interfaces this thing provides")


_cache = {}
def adaptISourceableToISource(sourceable):
    global _cache
    from garden.glue import Source
    if sourceable in _cache:
        return _cache[sourceable]
    result = _cache[sourceable] = Source(sourceable.sourceInterfaces)
    return result

components.registerAdapter(adaptISourceableToISource, ISourceable, ISource)



class IReceiver(Interface):


    def receiverMapping():
        """
        Get a mapping of interfaces to the functions that should respond to
        them.
        
        @return: A dict of the form::
        
            {
                IResult: self.resultReceived,
                ...
            }
        """



class IDataStore(Interface):


    def put(data):
        """
        Save data in the store.
        
        @type data: IData
        
        @rtype: C{Deferred}
        @return: On successful storage, will callback with a dictionary with
            at least the following items:
            
              - C{'changed'}: C{True} if C{value} is different than
                the previous value for the same C{(entity, name, version,
                lineage)}.  C{False} indicates that C{value} is the same.
            
            Acceptable values for errbacks are defined by specific
            implementations.
        """


    def get(entity, name=None, version=None, lineage=None):
        """
        Get data from the store
        
        @type entity: str
        @param entity: Entity name
        
        @type name: str
        @param name: Data name
        
        @type version: str
        @param version: Data version
        
        @type lineage: str
        @param lineage: Data lineal hash
        
        @rtype: C{Deferred}
        @return: On a successful fetch, this will callback with a list of tuples
            of the form C{(entity, name, version, lineage, value)} that match
            the passed in parameters.  If there are no matches, an empty list
            will be returned.
            
            Acceptable values for errbacks are defined by specific
            implementations.
        """



class IWorker(ISourceable, IReceiver):
    pass



class IGardener(ISourceable, IReceiver):
    pass



