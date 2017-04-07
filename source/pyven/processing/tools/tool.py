from pyven.processing.processible import Processible
from pyven.reporting.reportable import Reportable

class Tool(Processible, Reportable):
    
    def __init__(self, type, report, name, scope):
        Processible.__init__(self)
        Reportable.__init__(self, report)
        self.type = type
        self.name = name
        self.scope = scope

    def _format_call(self):
        raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "_format_call"')
    
    def clean(self, verbose=False):
        raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "clean"')

    