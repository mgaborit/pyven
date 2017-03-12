from pyven.reporting.content.line import Line
from pyven.reporting.style import Style

class Error(Line):

	def __init__(self, line):
		super(Error, self).__init__(line)
		self.div_style = Style.get().error['div_style']
		self.span_style = Style.get().error['span_style']
		