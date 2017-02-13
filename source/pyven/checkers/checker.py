import subprocess, os, logging, shutil, time

from pyven.exceptions.exception import PyvenException

from pyven.reporting.reportable import Reportable

logger = logging.getLogger('global')

class Checker(Reportable):

	def __init__(self, type):
		super(Checker, self).__init__()
		self.type = type
		
	def report_summary(self):
		return [self.type + ' checks']

	def report_identifiers(self):
		return self.report_summary()
	
	def report_properties(self):
		properties = []
		return properties
		
	def report_status(self):
		if len(self.errors) > 0:
			return 'FAILURE'
		else:
			return 'SUCCESS'
		
	def enabled(self):
		return len(self.errors) > 0
		