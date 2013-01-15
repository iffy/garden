from twisted.application import service, internet
from twisted.internet import endpoints, protocol
from twisted.python import usage



class Options(usage.Options):

    longdesc = 'Garden daemons live here'

    subCommands = [
        ('gardener', None, usage.Options, "Start a gardener server"),
    ]



def makeService(options):
    # See https://bitbucket.org/jerub/twisted-plugin-example/src/2baa0e726917/examplepackage/examplemodule.py?at=default
    print "I don't work yet"
    return simple.makeService(options.subOptions)