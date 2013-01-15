from twisted.python import usage
from twisted.internet import reactor, endpoints
from twisted.application import internet



class Options(usage.Options):

    optParameters = [
        ['endpoint', 'e', 'tcp:9990', "Endpoint on which to listen for workers"],
    ]



def makeService(options):
    """
    XXX
    """
    from garden.gardener import Gardener
    from garden.path import Garden
    from garden.local import InMemoryStore

    store = InMemoryStore()
    garden = Garden()
    gardener = Gardener(garden, store)
    
    # amp is currently the only option
    from garden.amp import GardenerFactory
    f = GardenerFactory()
    
    # connect them
    f.setResultReceiver(gardener)
    gardener.setWorkReceiver(f)
    
    endpoint = endpoints.serverFromString(reactor, options['endpoint'])
    service = internet.StreamServerEndpointService(endpoint, f)
    service.setName('Gardener Worker Server')
    return service