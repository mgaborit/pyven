import subprocess, os, shutil, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.reporting.reportable import Reportable

from pyven.logging.logger import Logger

class Tool(Processible, Reportable):
	TYPES = ['cmake', 'msbuild', 'makefile']
	SCOPES = ['preprocess', 'build']
	
	def __init__(self, type, name, scope):
		Processible.__init__(self)
		Reportable.__init__(self)
		self.type = type
		self.name = name
		self.scope = scope

	def _format_call(self):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "_format_call"')
	
	def clean(self, verbose=False):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "clean"')

	