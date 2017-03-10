from pyven.reporting.html_utils import HTMLUtils

class ErrorsGenerator(object):

	def __init__(self, errors=[]):
		self.errors = errors
		
	def generate(self):
		str = ''
		for error in self.errors:
			str += self._generate_error(error)
		return str
		
	@HTMLUtils.error
	def _generate_error(self, error):
		return error
		