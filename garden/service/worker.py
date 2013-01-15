from twisted.python import usage
from twisted.internet import reactor, endpoints
from twisted.application import service




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
        ['module', 'm', None, "Module containing Worker instance to use.  The "
                "module must contain a function named getWorker which returns "
                "a garden.interface.IWorker-implementing instance"]
    ]



def makeService(options):
    """
    XXX
    """
    from garden.worker import BlockingWorker
    worker = BlockingWorker()
    if options['module']:
        module = __import__(options['module'], globals(), locals(), ['getWorker'], -1)
        worker = module.getWorker()
    
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
