from pyven.reporting.content.line import Line
from pyven.reporting.style import Style

class Warning(Line):

	def __init__(self, line):
		super(Warning, self).__init__(line)
		self.div_style = Style.get().warning['div_style']
		self.span_style = Style.get().warning['span_style']
		