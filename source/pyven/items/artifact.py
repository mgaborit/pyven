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
	
	def check(self, version_checking):
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
					msg = ['Artifact version too short : ' + self.format_name(),\
							'Expected version : ' + self.version,\
							'Found version    : ' + '.'.join(actual_version)]
					version_checking.errors.append(msg)
					logger.error(msg[0])
					logger.error(msg[1])
					logger.error(msg[2])
					return False
				for idx, expected in enumerate(expected_version):
					if actual_version[idx] != expected:
						msg = ['Invalid artifact version : ' + self.format_name(),\
								'Expected version : ' + self.version,\
								'Found version    : ' + '.'.join(actual_version)]
						version_checking.errors.append(msg)
						logger.error(msg[0])
						logger.error(msg[1])
						logger.error(msg[2])
						return False
				return True
			except:
				msg = ['Artifact version not found : ' + self.format_name(), 'Expected version : ' + self.version]
				version_checking.errors.append(msg)
				logger.error(msg[0])
				logger.error(msg[1])
				return False
		else:
			return True