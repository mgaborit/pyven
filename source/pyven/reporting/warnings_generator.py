from pyven.reporting.html_utils import HTMLUtils

class WarningsGenerator(object):

	def __init__(self, warnings=[]):
		self.warnings = warnings
		
	def generate(self):
		str = ''
		for warning in self.warnings:
			str += self._generate_warning(warning)
		return str
		
	@HTMLUtils.warning
	def _generate_warning(self, warning):
		return warning
		