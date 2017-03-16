import pyven.constants
from pyven.reporting.content.reportable import ReportableListing
from pyven.reporting.content.lines import Lines
from pyven.reporting.content.error import Error
from pyven.reporting.content.warning import Warning
from pyven.reporting.content.title import Title
from pyven.reporting.content.properties import Properties
from pyven.reporting.content.success import Success
from pyven.reporting.content.failure import Failure
from pyven.reporting.content.unknown import Unknown

class Reportable(object):
	
	def __init__(self):
		self.status = pyven.constants.STATUS[2]
		self.errors = []
		self.warnings = []
		self.parser = None
	
	def status(self):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "status"')

	def content(self):
		lines = []
		for error in self.errors:
			lines.append(Error(error))
		for warning in self.warnings:
			lines.append(Warning(warning))
		content_lines = Lines(lines)
		return ReportableListing(title=Title(self.title()),\
								status=self.report_status(),\
								properties=Properties(self.properties()),\
								lines=content_lines)
		
	def title(self):
		raise NotImplementedError
		
	def properties(self):
		raise NotImplementedError
		
	def report_status(self):
		if self.status == pyven.constants.STATUS[0]:
			return Success()
		elif self.status == pyven.constants.STATUS[1]:
			return Failure()
		else:
			return Unknown()
	