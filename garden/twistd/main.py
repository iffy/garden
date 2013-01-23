"""
Things that use twistd plugins (daemons) are in here.
"""

from twisted.python import usage

from garden.twistd import combo



class Options(usage.Options):


    longdesc = ''

    subCommands = [
        ["combo", "c", combo.Options,
            "Launch a combination Gardener/Worker daemon."],
    ]



def makeService(options):
    """
    XXX
    """
    if options.subCommand == 'combo':
        return combo.makeService(options.subOptions)
    raise usage.UsageError("Unknown command")


