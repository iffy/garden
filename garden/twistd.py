from twisted.python import usage


from garden.service import gardener, worker


class Options(usage.Options):

    longdesc = 'Garden daemons live here'

    subCommands = [
        ('gardener', 'g', gardener.Options, "Start a gardener"),
        ('worker', 'w', worker.Options, "Start a worker"),
    ]



def makeService(options):
    # See https://bitbucket.org/jerub/twisted-plugin-example/src/2baa0e726917/examplepackage/examplemodule.py?at=default
    if options.subCommand == 'gardener':
        return gardener.makeService(options.subOptions)
    elif options.subCommand == 'worker':
        return worker.makeService(options.subOptions)
    print options