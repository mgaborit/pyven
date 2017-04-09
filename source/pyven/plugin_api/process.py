import pyven.constants
from pyven.reporting.content.reportable import ReportableListing
from pyven.reporting.content.lines import Lines
from pyven.reporting.content.error import Error
from pyven.reporting.content.warning import Warning
from pyven.reporting.content.title import Title
from pyven.reporting.content.property import Property
from pyven.reporting.content.properties import Properties
from pyven.reporting.content.success import Success
from pyven.reporting.content.failure import Failure
from pyven.reporting.content.unknown import Unknown

class Process(object):

    def __init__(self, cwd='.', name=None):
        self.cwd = cwd
        self.name = name
        self.type = None
        self.status = pyven.constants.STATUS[2]
        self.errors = []
        self.warnings = []
    
    def process(self, verbose=False, warning_as_error=False):
        raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "process"')
    
    def clean(self, verbose=False):
        raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "clean"')
    
    def report_content(self):
        lines = []
        for error in self.errors:
            lines.append(Error(error))
        for warning in self.warnings:
            lines.append(Warning(warning))
        content_lines = Lines(lines)
        properties = []
        for p in self.report_properties():
            properties.append(Property(name=p[0], value=p[1]))
        return ReportableListing(title=Title(self.title()),\
                                status=self.report_status(),\
                                properties=Properties(properties),\
                                lines=content_lines,\
                                summary=self.report_summary())

    def report_summary(self):
        raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "report_summary"')
    
    def report_title(self):
        raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "report_title"')
        
    def report_properties(self):
        raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "report_properties"')
        
    def report_status(self):
        if self.status == pyven.constants.STATUS[0]:
            return Success()
        elif self.status == pyven.constants.STATUS[1]:
            return Failure()
        else:
            return Unknown()
    