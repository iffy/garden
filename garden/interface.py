from zope.interface import Interface, Attribute



class IGardener(Interface):


    work_sender = Attribute("""An L{IWorkSender} instance""")


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


    def workReceived(entity, name, version, lineage, value, inputs):
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


    def workErrorReceived(entity, name, version, lineage, error, inputs):
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


class IInputReceiver(Interface):


    gardener = Attribute("""An L{IGardener} instance""")



class IResultReceiver(Interface):


    gardener = Attribute("""An L{IGardener} instance""")



class IWorkSender(Interface):


    def sendWork(entity, name, version, lineage, inputs):
        """
        Send a single unit of work through this sender.
        
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


class IWorkReceiver(Interface):


    worker = Attribute("""An L{IWorker} instance""")



class IWorker(Interface):


    sender = Attribute("""An L{IResultSender} instance""")


    def doWork(entity, name, version, lineage, inputs):
        """
        Do the work necessary to get the value of the destination.
        
        @type entity: str
        @param entity: Entity name
        
        @type name: str
        @param name: Result destination name
        
        @type version: str
        @param version: Result destination version
        
        @type lineage: str
        @param lineage: Result destination lineal hash
        
        @type inputs: list
        @param inputs: A list of input tuples needed to compute the destination.
            Each item is a tuple of the form::
            
                (name, version, lineage, value, hash)

        
        @return: A C{Deferred} which calls back once it is
            guaranteed that the result or resulting error will be passed to the
            sender.  In other words, this may callback before the result is
            computed.  The actual value of the callback is undefined.
            
            An errback indicates that this method should be called again (if
            the error is transient) or indicates a bug that should be fixed.
            In any case, if this errbacks, then the work B{WILL NOT} be
            completed.
        """



class IResultSender(Interface):


    def sendResult(entity, name, version, lineage, value, inputs):
        """
        Send a result.
        
        @type entity: str
        @param entity: Entity name
        
        @type name: str
        @param name: Result destination name
        
        @type version: str
        @param version: Result destination version
        
        @type lineage: str
        @param lineage: Result destination lineal hash
        
        @type value: str
        @param value: Result value
        
        @type inputs: list
        @param inputs: A list of input tuples used to compute the destination.
            Each item is a tuple of the form::
            
                (name, version, lineage, hash)
        
        
        @return: A C{Deferred} which calls back once it is guaranteed that the
            result will arrive at the destination (at some point).
            
            For instance, this may callback before a remote destination receives
            the result, but after this L{IResultSender} has persisted the
            request to send to the hard disk.

            If the result won't be delivered, this should errback to indicate
            that it should be attempted again.
        """


    def sendError(entity, name, version, lineage, error, inputs):
        """
        Send an error result.

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
        
        @return: A C{Deferred} which calls back once it is guaranteed that the
            error will arrive at the destination (at some point).
            
            For instance, this may callback before a remote destination receives
            the error, but after this L{IResultSender} has persisted the
            request to send to the hard disk.

            If the error won't be delivered, this should errback to indicate
            that it should be attempted again.
        """


