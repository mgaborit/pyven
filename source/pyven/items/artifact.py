import logging, os

from pyven.exceptions.exception import PyvenException
import pyven.constants

logger = logging.getLogger('global')

from pyven.items.item import Item

# pym.xml 'artifact' node
class Artifact(Item):

	def __init__(self, node):
		super(Artifact, self).__init__(node)
		self.file = None
		if not self.to_retrieve:
			self.file = node.text
	
	def type(self):
		return 'artifact'
	
	def basename(self):
		if self.file is not None:
			return os.path.basename(self.file)
		raise PyvenException('Unknown artifact location : ' + self.format_name())
	
	def check(self):
		if pyven.constants.PLATFORM == 'windows' and not self.to_retrieve:
			from win32api import GetFileVersionInfo, LOWORD, HIWORD
			expected_version = self.version.split('.')
			try:
				if not os.path.isfile(self.file):
					logger.error('Artifact not found : ' + self.format_name())
					return False
				info = GetFileVersionInfo(self.file, '\\')
				ms = info['FileVersionMS']
				ls = info['FileVersionLS']
				actual_version = [str(i) for i in [HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)]]
				if len(expected_version) > len(actual_version):
					logger.error('Artifact version too short : ' + self.format_name())
					logger.error('Expected version : ' + self.version)
					logger.error('Found version    : ' + '.'.join(actual_version))
					return False
				for idx, expected in enumerate(expected_version):
					if actual_version[idx] != expected:
						logger.error('Invalid artifact version : ' + self.format_name())
						logger.error('Expected version : ' + self.version)
						logger.error('Found version    : ' + '.'.join(actual_version))
						return False
				return True
			except:
				logger.error('Artifact version not found : ' + self.format_name())
				logger.error('Expected version : ' + self.version)
				return False
		else:
			return True