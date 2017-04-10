from pyven.exceptions.parser_exception import ParserException

class Parser(object):
    
    def __init__(self, cwd):
        self.cwd = cwd
    
    def parse_process(self, node):
        errors = []
        name = node.get('name')
        if name is None:
            errors.append('Missing process name')
        if len(errors) > 0:
            e = ParserException('')
            e.args = tuple(errors)
            raise e
        return name,
  
    def parse(self, node, project):
        raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "parse"')