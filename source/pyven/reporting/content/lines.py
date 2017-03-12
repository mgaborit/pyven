import os
from string import Template

from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.utils import str_to_file, file_to_str
from pyven.reporting.content.content import Content
from pyven.reporting.style import Style

class Lines(Content):
	TEMPLATE = os.path.join(Content.TEMPLATE_DIR, 'lines-template.html')
	NB_LINES = 10

	def __init__(self, lines=[]):
		super(Lines, self).__init__()
		self.lines = lines
		self.div_style = Style.get().lines['div_style']
		
	def write(self):
		Lines.generate_template()
		return self.write_lines()
	
	def write_lines(self):
		result = ''
		if len(self.lines) > 0:
			i = 0
			while i < Lines.NB_LINES and i < len(self.lines):
				result += self.lines[i].write()
				i += 1
			template = Template(file_to_str(Lines.TEMPLATE))
			result = template.substitute(VALUE=result, DIV_STYLE=self.div_style)
		return result
	
	@staticmethod
	def generate_template():
		if not os.path.isdir(Content.TEMPLATE_DIR):
			os.makedirs(Content.TEMPLATE_DIR)
		if not os.path.isfile(Lines.TEMPLATE):
			str_to_file(Lines.generate_template_lines(), Lines.TEMPLATE)
	
	@staticmethod
	def generate_template_lines():
		html_str = HTMLUtils.ltag('div', {'class' : '$DIV_STYLE'})
		try:
			html_str += '$VALUE'
		finally:
			html_str += HTMLUtils.rtag('div')
		return html_str
