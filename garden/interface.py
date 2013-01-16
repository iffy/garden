from zope.interface import Interface, Attribute



class IDataStore(Interface):


    def put(entity, name, version, lineage, value):
        """
        Save data in the store.
        
        @type entity: str
        @param entity: Entity name
        
        @type name: str
        @param name: Data name
        
        @type version: str
        @param version: Data version
        
        @type lineage: str
        @param lineage: Data lineal hash
        
        @type value: str
        @param value: Data value
        
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


class IInputSource(Interface):


    input_receiver = Attribute("""
        L{IInputReceiver} set by L{setInputReceiver}
        """)


    def setInputReceiver(receiver):
        """
        Choose the L{IInputReceiver} to receive input from this source.
        """



class IInputReceiver(Interface):


    def inputReceived(entity, name, version, value):
        """
        Data received from an outside source.
        
        @type entity: str
        @param entity: Entity name
        
        @type name: str
        @param name: Data name
        
        @type version: str
        @param version: Data version
        
        @type value: str
        @param value: Data value
        
        @return: A L{Deferred} which fires to acknowledge receipt of the input.
            Errback indicates the data was not received and should be sent
            again.
        """



class IResultSource(Interface):


    result_receiver = Attribute("""
        L{IResultReceiver} set by L{setResultReceiver}
        """)


    def setResultReceiver(receiver):
        """
        Choose the L{IResultReceiver} to receive results from this source.
        """



class IResultReceiver(Interface):


    def resultReceived(entity, name, version, lineage, value, inputs):
        """
        Called when a work result is received.
        
        @type entity: str
        @param entity: Entity name
        
        @type name: str
        @param name: Data name
        
        @type version: str
        @param version: Data version
        
        @type lineage: str
        @param lineage: Data lineage
        
        @type value: str
        @param value: Data value
        
        @type inputs: list
        @param inputs: A list of the input tuples used to compute the data.
            Each item is a tuple of the form::
            
                (name, version, lineage, hash)
        
        @return: A L{Deferred} which fires to acknowledge receipt of the data.
            Errback indicates the data was not received and should be sent
            again.
        """


    def resultErrorReceived(entity, name, version, lineage, error, inputs):
        """
        Called to report an error that happened while doing some work.

        @type entity: str
        @param entity: Entity name
        
        @type name: str
        @param name: Result destination name
        
        @type version: str
        @param version: Result destination version
        
        @type lineage: str
        @param lineage: Result destination lineal hash
        
        @type error: str
        @param error: Error message (could be a JSON string)
        
        @type inputs: list
        @param inputs: A list of input tuples used to compute the destination.
            Each item is a tuple of the form::
            
                (name, version, lineage, hash)

        @return: A L{Deferred} which fires to acknowledge receipt of the error.
            Errback indicates the error was not received and should be sent
            again.
        """



class IWorkSource(Interface):


    work_receiver = Attribute("""
        L{IWorkReceiver} set by L{setWorkReceiver}
        """)


    def setWorkReceiver(receiver):
        """
        Choose the L{IWorkReceiver} to receive the results from this source.
        """



class IWorkReceiver(Interface):


    def workReceived(entity, name, version, lineage, inputs):
        """
        Receive a single piece of work.
        
        @type entity: str
        @param entity: Entity name
        
        @type name: str
        @param name: Destination name
        
        @type version: str
        @param version: Destination version
        
        @type lineage: str
        @param lineage: Destination lineal hash
        
        @type inputs: list
        @param inputs: A list of input tuples needed to compute the destination.
            Each item is a tuple of the form::
            
                (name, version, lineage, value, hash)
        
        @return: A C{Deferred} which fires once the work has been "received."
            It is up to the sender to define what "received" means, with the
            hope that once a piece of work is considered "received," the work
            is guaranteed to be completed by a worker.
            
            If the work is not successfully received, the C{Deferred} should
            errback.
        """



class IWorker(IWorkReceiver, IResultSource):
    pass



class IGardener(IResultReceiver, IInputReceiver, IWorkSource):
    pass



