from threading import Event

event_registry = None

class Events:
    """Class for broadcasting event messages, which are picked up by registered functions."""
    hooks = {}
    event_locks = {}
    disabled = False
    @staticmethod
    def retrieve():
        """ Retrieves a singleton instance, and creates it if it doesn't exist. """
        global event_registry
        if event_registry is None:
            event_registry = Events()
        return event_registry
    
    def wait_for(self, token):
        self.event_locks.setdefault(token, Event())
        event = self.event_locks.setdefault(token, Event())
        event.wait()
    
    def listen(self, token, func):
        self.hooks.setdefault(token, [])
        if func not in self.hooks[token]:
            self.hooks[token].append(func)
    
    def unlisten(self, token, func):
        if token in self.hooks:
            while func in self.hooks[token]:
                self.hooks[token].remove(func)
        
    def send(self, token):
        if not self.disabled:
            #print "Event {} announced.".format(token)
            
            # release waiting threads
            event = self.event_locks.setdefault(token, Event())
            event.set()
            event.clear()
            
            # call registered functions
            if token in self.hooks:
                #print "Functions called: ", repr(self.hooks[token])
                for func in self.hooks[token]:
                    func()
    
    def disable(self):
        """to be done at the end of the piece"""
        self.disabled = True
    
    def __init__(self):
        pass

def test():
    print 'testing'

if __name__ == '__main__':
    events = Events.retrieve()
    events.listen('calltest', test)
    events.send('calltest')
    
    