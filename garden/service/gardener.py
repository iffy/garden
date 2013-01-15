from twisted.python import usage
from twisted.internet import reactor, endpoints, protocol
from twisted.protocols import basic
from twisted.application import internet, service



class Options(usage.Options):

    optParameters = [
        ['worker-endpoint', 'e', 'tcp:9990', "Endpoint on which to listen for workers"],
        ['input-endpoint', 'd', 'tcp:9991', "Endpoint on which to listen for input"],
        ['module', 'm', None, "Module containing Garden instance to use.  The "
                "module must contain a function named getGarden which returns "
                "a garden.path.Garden instance"],
    ]



class DataReceiver(basic.StatefulStringProtocol, basic.NetstringReceiver):

    state = 'entity'


    def proto_entity(self, entity):
        self.entity = entity
        return 'name'
    
    def proto_name(self, name):
        self.name = name
        return 'version'
    
    def proto_version(self, version):
        self.version = version
        return 'value'
    
    def proto_value(self, value):
        self.value = value
        r = self.factory.input_receiver.inputReceived(self.entity, self.name, self.version, self.value)
        r.addBoth(self.done)
        return 'wait'

    def proto_wait(self, ignore):
        return 'wait'

    def done(self, result):
        print 'Got data: entity=%r name=%r version=%r value=%r' % (self.entity, self.name, self.version, self.value)
        self.transport.loseConnection()



class DataReceiverFactory(protocol.Factory):

    protocol = DataReceiver

    def __init__(self, input_receiver):
        self.input_receiver = input_receiver



def makeService(options):
    """
    XXX
    """
    from garden.gardener import Gardener
    from garden.path import Garden
    from garden.local import InMemoryStore

    # get a Garden
    garden = Garden()
    if options['module']:
        module = __import__(options['module'], globals(), locals(), ['getGarden'], -1)
        garden = module.getGarden()

    # XXX InMemoryStore is the only option right now
    store = InMemoryStore()
    gardener = Gardener(garden, store)
    
    # amp is currently the only option
    from garden.amp import GardenerFactory
    f = GardenerFactory()
    
    # connect them
    f.setResultReceiver(gardener)
    gardener.setWorkReceiver(f)
    
    endpoint = endpoints.serverFromString(reactor, options['worker-endpoint'])
    worker_service = internet.StreamServerEndpointService(endpoint, f)
    worker_service.setName('Gardener Worker Server')
    
    # listen for data
    input_f = DataReceiverFactory(gardener)
    endpoint = endpoints.serverFromString(reactor, options['input-endpoint'])
    input_service = internet.StreamServerEndpointService(endpoint, input_f)
    input_service.setName('Input Service')
    
    ms = service.MultiService()
    worker_service.setServiceParent(ms)
    input_service.setServiceParent(ms)
    
    return ms