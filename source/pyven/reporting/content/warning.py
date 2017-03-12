from pyven.reporting.content.line import Line
from pyven.reporting.style import Style

class Warning(Line):

	def __init__(self, line):
		super(Warning, self).__init__(line)
		self.type_style = Style.get().line['warning']
		