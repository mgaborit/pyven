from pyven.reporting.html_utils import HTMLUtils

from pyven.reporting.generator import Generator

class ErrorsGenerator(Generator):

	def __init__(self, errors=[]):
		super(ErrorsGenerator, self).__init__()
		if len(errors) > Generator.NB_LINES:
			errors = errors[:Generator.NB_LINES]
		self.errors = errors
		
	def generate(self):
		str = ''
		for error in self.errors:
			str += self._generate_error(error)
		return str
		
	@HTMLUtils.error
	def _generate_error(self, error):
		return error
		