import os
from string import Template

from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.utils import file_to_str, str_to_file
from pyven.reporting.style import Style
from pyven.reporting.content.content import Content

class Line(Content):
	TEMPLATE_LINE = os.path.join(Content.TEMPLATE_DIR, 'line-template.html')
	TEMPLATE_PART = os.path.join(Content.TEMPLATE_DIR, 'line-part-template.html')

	def __init__(self, line):
		super(Line, self).__init__()
		self.line = line
		self.div_style = Style.get().line['div_style']
		self.part_style = Style.get().line['part_style']
		self.type_style = ''

	def write(self):
		Line.generate_template()
		return self.write_line()
		
	def write_line(self):
		result = ''
		for part in self.line:
			result += self.write_part(part)
		template = Template(file_to_str(self.TEMPLATE_LINE))
		return template.substitute(VALUE=result,\
									DIV_STYLE=' '.join([self.div_style, self.type_style]))
		
	def write_part(self, part):
		template = Template(file_to_str(self.TEMPLATE_PART))
		return template.substitute(VALUE=part, PART_STYLE=' '.join([self.part_style, self.type_style]))
		
	@staticmethod
	def generate_template():
		if not os.path.isdir(Content.TEMPLATE_DIR):
			os.makedirs(Content.TEMPLATE_DIR)
		if not os.path.isfile(Line.TEMPLATE_LINE) or not os.path.isfile(Line.TEMPLATE_PART):
			str_to_file(Line.generate_template_line(), Line.TEMPLATE_LINE)
			str_to_file(Line.generate_template_part(), Line.TEMPLATE_PART)
	
	@staticmethod
	def generate_template_line():
		html_str = HTMLUtils.ltag('div', {'class' : '$DIV_STYLE'})
		try:
			html_str += '$VALUE'
		finally:
			html_str += HTMLUtils.rtag('div')
		return html_str
	
	@staticmethod
	def generate_template_part():
		html_str = HTMLUtils.ltag('p', {'class' : '$PART_STYLE'})
		try:
			html_str += '$VALUE'
		finally:
			html_str += HTMLUtils.rtag('p')
		return html_str
		
	