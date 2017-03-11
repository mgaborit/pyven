from pyven.reporting.html_utils import HTMLUtils

from pyven.reporting.generator import Generator

class WarningsGenerator(Generator):

	def __init__(self, warnings=[]):
		super(WarningsGenerator, self).__init__()
		if len(warnings) > Generator.NB_LINES:
			warnings = warnings[:Generator.NB_LINES]
		self.warnings = warnings
		
	def generate(self):
		str = ''
		for warning in self.warnings:
			str += self._generate_warning(warning)
		return str
		
	@HTMLUtils.warning
	def _generate_warning(self, warning):
		return warning
		