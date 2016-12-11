import subprocess, os, logging, shutil, time

from pyven.exceptions.exception import PyvenException

from pyven.processing.processible import Processible
from pyven.reporting.reportable import Reportable

logger = logging.getLogger('global')

# pym.xml 'tool' node
class Tool(Processible, Reportable):
	TYPES = ['cmake', 'msbuild', 'makefile']
	SCOPES = ['preprocess', 'build']
	
	def __init__(self, node):
		Processible.__init__(self)
		Reportable.__init__(self)
		self.type = node.get('type')
		if self.type is None:
			raise PyvenException('Missing tool type')
		if self.type not in Tool.TYPES:
			raise PyvenException('Wrong tool type : ' + self.type, 'Available tools : ' + str(Tool.TYPES))
		self.name = node.get('name')
		if self.name is None:
			raise PyvenException('Missing tool name')
		self.scope = node.get('scope')
		if self.scope is None:
			raise PyvenException('Missing tool scope')
		if self.scope not in Tool.SCOPES:
			raise PyvenException('Wrong tool scope : ' + self.scope, 'Available scopes : ' + str(Tool.SCOPES))

	def report_status(self):
		return self.status
		
	def _format_call(self):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "_format_call"')
	
	def clean(self, verbose=False):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "clean"')

	