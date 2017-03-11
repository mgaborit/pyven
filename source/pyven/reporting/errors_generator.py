import os

from pyven.reporting.html_utils import HTMLUtils
from string import Template

from pyven.utils.utils import str_to_file, file_to_str

from pyven.reporting.generator import Generator

class ErrorsGenerator(Generator):
	TEMPLATE_FILE = 'items-template.html'
	TEMPLATE_FILE_ITEM = 'item-template.html'

	def __init__(self, errors=[], warnings=[]):
		super(ErrorsGenerator, self).__init__()
		tmp = errors + warnings
		tmp_errors = []
		tmp_warnings = []
		i = 0
		while i < Generator.NB_LINES and i < len(tmp):
			item = tmp[i]
			if item in errors:
				tmp_errors.append(item)
			else:
				tmp_warnings.append(item)
			i += 1
		self.errors = tmp_errors
		self.warnings = tmp_warnings
		
	def write(self):
		ErrorsGenerator.generate_template()
		return self.write_items('error') + self.write_items('warning')
	
	def write_items(self, type):
		items = []
		div_style = ''
		span_style = ''
		if type == 'error':
			items = self.errors
			div_style = HTMLUtils.STYLE.error['div']
			span_style = HTMLUtils.STYLE.error['error']
		else:
			items = self.warnings
			div_style = HTMLUtils.STYLE.warning['div']
			span_style = HTMLUtils.STYLE.warning['warning']
		str = ''
		if len(items) > 0:
			for item in items:
				str += self.write_item(item)
			template = Template(file_to_str(os.path.join(HTMLUtils.TEMPLATE_DIR, ErrorsGenerator.TEMPLATE_FILE)))
			str = template.substitute(DIV_STYLE=div_style, SPAN_STYLE=span_style, VALUE=str)
		return str
	
	def write_item(self, item):
		str = ''
		template = Template(file_to_str(os.path.join(HTMLUtils.TEMPLATE_DIR, ErrorsGenerator.TEMPLATE_FILE_ITEM)))
		for part in item:
			str += template.substitute(VALUE=part)
		return str
		
	
	@staticmethod
	def generate_template():
		if not os.path.isdir(HTMLUtils.TEMPLATE_DIR):
			os.makedirs(HTMLUtils.TEMPLATE_DIR)
		str_to_file(ErrorsGenerator.generate_items(), os.path.join(HTMLUtils.TEMPLATE_DIR, ErrorsGenerator.TEMPLATE_FILE))
		str_to_file(ErrorsGenerator.generate_item(), os.path.join(HTMLUtils.TEMPLATE_DIR, ErrorsGenerator.TEMPLATE_FILE_ITEM))

	@staticmethod
	def generate_items():
		html_str = HTMLUtils.ltag('div', {'class' : '$DIV_STYLE'})
		try:
			html_str += HTMLUtils.ltag('span', {'class' : '$SPAN_STYLE'})
			try:
				html_str += '$VALUE'
			finally:
				html_str += HTMLUtils.rtag('span')
		finally:
			html_str += HTMLUtils.rtag('div')
		return html_str
		
	@staticmethod
	def generate_item():
		html_str = HTMLUtils.ltag('p')
		try:
			html_str += '$VALUE'
		finally:
			html_str += HTMLUtils.rtag('p')
		return html_str
		