class Gardener(object):
    """
    I coordinate work based on new data.
    """
    
    
    def __init__(self, garden, store, dispatcher, accept_all_lineages):
        self.garden = garden
        self.store = store
        self.dispatcher = dispatcher
        self.accept_all_lineages = accept_all_lineages