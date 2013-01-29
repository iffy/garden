from twisted.python import usage, reflect, log
from twisted.internet import reactor, endpoints
from twisted.application import internet

from garden.interface import IWorker, ISource
from garden.path import Garden
from garden.gardener import Gardener


class Options(usage.Options):
    
    optParameters = [
        ['module', 'm', None, "Module containing getGarden() and getWorker()"
            " functions"],
        ['sqlite-db', None, ":memory:", "SQLite database name"],
        ['http-input-endpoint', 'w', 'tcp:9990',
            "Endpoint on which to have the HTTP InputSource receive input"],
    ]
    
    def postOptions(self):
        if not self['module']:
            # this is hoped to be a temporary requirement (which is why the
            # module option is an option and not an arg in the first place)
            raise usage.UsageError("You must specify a module")



def makeService(options):
    """
    XXX
    """
    module = reflect.namedModule(options['module'])
    
    # worker
    worker = IWorker(module.getWorker())
    
    # garden
    garden = module.getGarden()
    assert isinstance(garden, Garden)
    
    # store
    from garden.store import SqliteStore
    sqlite_uri = options['sqlite-db']
    log.msg('SqliteStore(%r)' % (sqlite_uri,))
    store = SqliteStore(sqlite_uri)
    
    # http input/output
    from garden.http import WebInputSource, WebDataFeed
    from twisted.web.resource import Resource
    from twisted.web.server import Site
    http_input_source = WebInputSource()
    http_data_receiver = WebDataFeed()
    root = Resource()
    root.putChild('', http_input_source)
    root.putChild('feed', http_data_receiver)
    site = Site(root)
    
    endpoint = endpoints.serverFromString(reactor,
                                          options['http-input-endpoint'])
    http_service = internet.StreamServerEndpointService(endpoint, site)
    
    # gardener
    gardener = Gardener(garden, store)
    
    # hook them all together
    gardener.subscribe(worker)
    ISource(worker).subscribe(gardener)
    ISource(http_input_source).subscribe(gardener)
    gardener.subscribe(http_data_receiver)
    
    return http_service


