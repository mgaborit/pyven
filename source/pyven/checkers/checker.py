from pyven.exceptions.exception import PyvenException

from pyven.reporting.reportable import Reportable
from pyven.reporting.content.success import Success
from pyven.reporting.content.failure import Failure

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
		return {}
	
	def report_status(self):
		if self.enabled():
			return Failure()
		else:
			return Success()