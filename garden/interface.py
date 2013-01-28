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



class IDataSource(Interface):
    """
    I am a source of data (input + lineal hash)
    """
    
    def setDataReceiver(receiver):
        """
        Set the L{IDataReceiver} to receive data from me.
        """



class IDataReceiver(Interface):
    """
    I receive data (input + lineal hash)
    """
    
    def dataReceived(data):
        """
        Receive the passed in data.
        
        @type data: IData
        
        @return: A C{Deferred} which callbacks to indicate receipt of the data
            and errbacks to indicate data not received.
        """


class IInputSource(Interface):



    def setInputReceiver(receiver):
        """
        Choose the L{IInputReceiver} to receive input from this source.
        """



class IInputReceiver(Interface):


    def inputReceived(input_data):
        """
        Data received from an outside source.
        
        @type input_data: IInput
        
        @return: A L{Deferred} which fires to acknowledge receipt of the input.
            Errback indicates the data was not received and should be sent
            again.
        """



class IResultSource(Interface):


    def setResultReceiver(receiver):
        """
        Choose the L{IResultReceiver} to receive results from this source.
        """



class IResultReceiver(Interface):


    def resultReceived(result):
        """
        Called when a work result is received.
        
        @type result: IResult
        
        @return: A L{Deferred} which fires to acknowledge receipt of the data.
            Errback indicates the data was not received and should be sent
            again.
        """



class IResultErrorSource(Interface):


    def setResultErrorReceiver(receiver):
        """
        Choose the L{IResultErrorReceiver} to receive results from this source.
        """



class IResultErrorReceiver(Interface):


    def resultErrorReceived(error):
        """
        Called to report an error that happened while doing some work.

        @type error: IResultError

        @return: A L{Deferred} which fires to acknowledge receipt of the error.
            Errback indicates the error was not received and should be sent
            again.
        """



class IWorkSource(Interface):


    def setWorkReceiver(receiver):
        """
        Choose the L{IWorkReceiver} to receive the results from this source.
        """



class IWorkReceiver(Interface):


    def workReceived(work):
        """
        Receive a single piece of work.
        
        @type work: IWork
        
        @return: A C{Deferred} which fires once the work has been "received."
            It is up to the sender to define what "received" means, with the
            hope that once a piece of work is considered "received," the work
            is guaranteed to be completed by a worker.
            
            If the work is not successfully received, the C{Deferred} should
            errback.
        """



class IWorker(IWorkReceiver, IResultSource, IResultErrorSource):
    pass



class IGardener(IResultReceiver, IResultErrorReceiver, IDataSource,
                IInputReceiver, IWorkSource):
    pass



