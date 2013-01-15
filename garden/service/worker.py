from twisted.python import usage
from twisted.internet import reactor, endpoints, protocol
from twisted.application import internet, service




class StreamClientEndpointService(service.Service, object):


    def __init__(self, endpoint, factory):
        self.endpoint = endpoint
        self.factory = factory


    def startService(self):
        service.Service.startService(self)
        self.endpoint.connect(self.factory)



class Options(usage.Options):

    optParameters = [
        ['endpoint', 'e', 'tcp:127.0.0.1:9990',
            "Endpoint of gardener to connect to for work"],
    ]



def makeService(options):
    """
    XXX
    """
    from garden.worker import BlockingWorker
    worker = BlockingWorker()
    
    # amp is currently the only option
    from garden.amp import WorkerFactory
    f = WorkerFactory()
    
    # connect them
    f.setWorkReceiver(worker)
    worker.setResultReceiver(f)
    
    endpoint = endpoints.clientFromString(reactor, options['endpoint'])
    service = StreamClientEndpointService(endpoint, f)
    service.setName('Worker')
    return service