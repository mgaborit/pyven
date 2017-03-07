import os, logging
from pyven.exceptions.exception import PyvenException

logger = logging.getLogger('global')

class Step(object):
	WORKSPACE = None

	def __init__(self, path='', verbose=False):
		self.path = path
		self.verbose = verbose
		self.name = None
		self.checker = None

	def log_path(self):
		result = ''
		if self.path != '':
			result = '[' + self.path + '] '
		return result
		
	def log_delimiter(self):
		logger.info(self.log_path() + '===================================')
	
	@staticmethod
	def error_checks(function):
		def _intern(self):
			self.log_delimiter()
			logger.info(self.log_path() + 'STEP ' + self.name.replace('_', '').upper() + ' : STARTING')
			self.log_delimiter()
			ok = True
			try:
				if self.path != '':
					if not os.path.isdir(self.path):
						raise PyvenException('Subproject path does not exist : ' + self.path)
					os.chdir(self.path)
				ok = function(self)
				if self.path != '':
					for dir in self.path.split(os.sep):
						os.chdir('..')
			except PyvenException as e:
				for msg in e.args:
					self.checker.errors.append(msg)
				ok = False
			if ok:
				self.log_delimiter()
				logger.info(self.log_path() + 'STEP ' + self.name.replace('_', '').upper() + ' : SUCCESSFUL')
				self.log_delimiter()
			else:
				self.log_delimiter()
				logger.info(self.log_path() + 'STEP ' + self.name.replace('_', '').upper() + ' : FAILED')
				self.log_delimiter()
			return ok
		return _intern
		
	def process(self):
		raise NotImplementedError
	