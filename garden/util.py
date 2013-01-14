class RoundRobinChooser(object):
    """
    XXX
    """
    
    
    def __init__(self):
        self.options = []
        self._gen = self._makeGen()


    def _makeGen(self):
        while True:
            for x in self.options:
                yield x


    def add(self, option):
        """
        XXX
        """
        self.options.append(option)


    def remove(self, option):
        """
        XXX
        """
        self.options.remove(option)


    def next(self):
        """
        XXX
        """
        if not self.options:
            raise IndexError("No options to choose from")
        return self._gen.next()