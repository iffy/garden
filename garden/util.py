class RoundRobinChooser(object):
    """
    I choose among a group of options by cycling through them.
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
        Add an option to the rotation.
        
        @param option: Value of option.
        """
        self.options.append(option)


    def remove(self, option):
        """
        Remove an option from the rotation.
        
        @param option: Option to remove.
        """
        self.options.remove(option)


    def next(self):
        """
        Get the next option.
        
        @raise IndexError: If there's no option to get.
        
        @return: The next option.
        """
        if not self.options:
            raise IndexError("No options to choose from")
        return self._gen.next()