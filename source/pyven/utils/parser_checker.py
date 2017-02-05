import subprocess, os, logging, shutil, time

from pyven.exceptions.exception import PyvenException

from pyven.reporting.reportable import Reportable

logger = logging.getLogger('global')

class ParserChecker(Reportable):

	def __init__(self):
		super(ParserChecker, self).__init__()
		self.enabled = False
		
	def report_summary(self):
		return ['Pym parsing']

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
		