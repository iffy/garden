from collections import defaultdict
from hashlib import sha1


from garden.error import Error



class CycleError(Error):
    pass
    



def linealHash(name, version, input_hashes=None):
    """
    Compute a hash to describe the lineage of a particular garden destination.
    
    @param name: Destination name
    @param version: Destination version
    
    @param input_hashes: If the data point identified by the C{name}, C{version}
        pair is a destination of a garden path, then C{input_hashes} is the
        list of lineal hashes of the garden path's inputs.  For instance, if
        this garden path was defined::
        
            garden.addPath('cake', '1', [
                ('eggs', '1'),
                ('flour', '1'),
            ])
        
        And both C{('eggs', '1')} and C{('flour', '1')} do not require any
        inputs, then to compute the lineal hash of C{('cake', '1')}, do this::
        
            linealHash('cake', '1', [
                linealHash('eggs', '1'),
                linealHash('flour', '1'),
            ])
        
        If C{('flour', '1')} required input C{('wheat', '1')} then you would
        instead do this::
        
            linealHash('cake', '1', [
                linealHash('eggs', '1'),
                linealHash('flour', '1', [
                    linealHash('wheat', '1'),
                ]),
            ])
    """
    basic = sha1(sha1(name).hexdigest() + version).hexdigest()
    if not input_hashes:
        return basic
    
    # destination has inputs
    parts = [basic] + input_hashes
    return sha1(''.join(parts)).hexdigest()



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
        
        @return: A list of 2-tuples (name, version) of inputs needed to reach
            the given destination.
        """
        return self._destinations[(name, version)]



