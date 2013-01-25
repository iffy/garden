from collections import defaultdict


from garden.error import Error



class CycleError(Error):
    pass



class Garden(object):
    """
    I am a garden of forking paths.
    """
    
    
    def __init__(self):
        self._destinations = defaultdict(lambda:[])
        self._inputs = defaultdict(lambda:[])
    
    
    def addPath(self, name, version, inputs):
        """
        @param name: Destination name
        @param version: Destination version
        @param inputs: Inputs required for destination.  Must be an list of
            2-tuples (name, version).
        
        @raise CycleError: If adding this path would create circular
            dependencies/recursion.
        """
        if (name, version) in inputs:
            raise CycleError(name, version, inputs)
        
        def ancestors(n, v):
            input_lists = self.inputsFor(n, v)
            for input_list in input_lists:
                for i in input_list:
                    yield i
                    for x in ancestors(*i):
                        yield x
        # check each input line
        for i in inputs:
            if (name, version) in ancestors(*i):
                raise CycleError(name, version, inputs)

        self._destinations[(name, version)].append(inputs)
        for iname, iversion in inputs:
            self._inputs[(iname, iversion)].append((name, version))


    def pathsRequiring(self, name, version):
        """
        @param name: Input name
        @param version: Input version
        
        @return: A list of 2-tuples (name, version) of destinations requiring
            the given input. 
        """
        return self._inputs[(name, version)]


    def inputsFor(self, name, version):
        """
        Get the inputs needed for a particular destination.
        
        @param name: Destination name
        @param version: Destination version
        
        @return: A list of lists of 2-tuples (name, version) of inputs needed
            to reach the given destination.
        """
        return self._destinations[(name, version)]



