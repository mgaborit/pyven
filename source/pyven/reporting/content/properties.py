import os
from string import Template

from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.utils import str_to_file, file_to_str
from pyven.reporting.content.content import Content
from pyven.reporting.style import Style

class Properties(Content):
	TEMPLATE = os.path.join(Content.TEMPLATE_DIR, 'properties-template.html')

	def __init__(self, properties=[]):
		super(Properties, self).__init__()
		self.properties = properties
		self.div_style = Style.get().properties['div_style']
		
	def write(self):
		Properties.generate_template()
		return self.write_properties()
	
	def write_properties(self):
		result = ''
		if len(self.properties) > 0:
			for property in self.properties:
				result += property.write()
			template = Template(file_to_str(Properties.TEMPLATE))
			result = template.substitute(VALUE=result, DIV_STYLE=self.div_style)
		return result
	
	@staticmethod
	def generate_template():
		if not os.path.isdir(Content.TEMPLATE_DIR):
			os.makedirs(Content.TEMPLATE_DIR)
		if not os.path.isfile(Properties.TEMPLATE):
			str_to_file(Properties.generate_template_properties(), Properties.TEMPLATE)
	
	@staticmethod
	def generate_template_properties():
		html_str = HTMLUtils.ltag('div', {'class' : '$DIV_STYLE'})
		try:
			html_str += '$VALUE'
		finally:
			html_str += HTMLUtils.rtag('div')
		return html_str
