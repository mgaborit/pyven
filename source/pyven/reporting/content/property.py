import os
from string import Template

from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.utils import str_to_file, file_to_str
from pyven.reporting.content.content import Content
from pyven.reporting.style import Style

class Property(Content):
	TEMPLATE = os.path.join(Content.TEMPLATE_DIR, 'property-template.html')

	def __init__(self, name, value):
		super(Property, self).__init__()
		self.name = name
		self.value = value
		self.p_style = Style.get().property['p_style']
		
	def write(self):
		Property.generate_template()
		return self.write_property()
	
	def write_property(self):
		template = Template(file_to_str(Property.TEMPLATE))
		result = template.substitute(NAME=self.name, VALUE=self.value, P_STYLE=self.p_style)
		return result
	
	@staticmethod
	def generate_template():
		if not os.path.isdir(Content.TEMPLATE_DIR):
			os.makedirs(Content.TEMPLATE_DIR)
		if not os.path.isfile(Property.TEMPLATE):
			str_to_file(Property.generate_template_property(), Property.TEMPLATE)
	
	@staticmethod
	def generate_template_property():
		html_str = HTMLUtils.ltag('p', {'class' : '$P_STYLE'})
		try:
			html_str += '$NAME : $VALUE' 
		finally:
			html_str += HTMLUtils.rtag('p')
		return html_str
