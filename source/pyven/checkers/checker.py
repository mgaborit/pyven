from pyven.exceptions.exception import PyvenException

from pyven.reporting.reportable import Reportable

class Checker(Reportable):

	def __init__(self, type):
		super(Checker, self).__init__()
		self.type = type
		self.status = 'UNKNOWN'
		
	def enabled(self):
		return len(self.errors) > 0
		
	def title(self):
		return self.type + ' checks'
		
	def properties(self):
		properties = {}
		properties['Status'] = self.status
		return properties