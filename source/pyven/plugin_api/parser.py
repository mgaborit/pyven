class Parser(object):
    
    def __init__(self, cwd):
        self.cwd = cwd
        
    def parse(self, node):
        raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "parse"')