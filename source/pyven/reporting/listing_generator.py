import os
from string import Template

from pyven.utils.utils import str_to_file, file_to_str

from pyven.reporting.html_utils import HTMLUtils

from pyven.reporting.generator import Generator

class ListingGenerator(Generator):
	TEMPLATE_FILE_LISTING = 'listing-template.html'
	TEMPLATE_FILE_PROPERTY = 'property-template.html'
	TEMPLATE_FILE_STATUS = 'status-template.html'

	def __init__(self, title, properties={}, generators=[]):
		super(ListingGenerator, self).__init__()
		self.title = title
		self.properties = properties
		self.generators = generators
		
	@staticmethod
	def generate_template():
		if not os.path.isdir(HTMLUtils.TEMPLATE_DIR):
			os.makedirs(HTMLUtils.TEMPLATE_DIR)
		str_to_file(ListingGenerator.generate_listing(), os.path.join(HTMLUtils.TEMPLATE_DIR, ListingGenerator.TEMPLATE_FILE_LISTING))
		str_to_file(ListingGenerator.generate_property(), os.path.join(HTMLUtils.TEMPLATE_DIR, ListingGenerator.TEMPLATE_FILE_PROPERTY))
		str_to_file(ListingGenerator.generate_status(), os.path.join(HTMLUtils.TEMPLATE_DIR, ListingGenerator.TEMPLATE_FILE_STATUS))
	
	@staticmethod
	def generate_listing():
		html_str = HTMLUtils.ltag('div', {'class' : HTMLUtils.STYLE.listing['div']})
		try:
			html_str += HTMLUtils.ltag('h2')
			try:
				html_str += '$TITLE'
			finally:
				html_str += HTMLUtils.rtag('h2')
			html_str += HTMLUtils.ltag('div', {'class' : HTMLUtils.STYLE.listing['properties']['div']})
			try:
				html_str += '$PROPERTIES'
			finally:
				html_str += HTMLUtils.rtag('div')
			html_str += '$LISTING'
		finally:
			html_str += HTMLUtils.rtag('div')
		return html_str

	@staticmethod
	def generate_property():
		html_str = HTMLUtils.ltag('p', {'class' : HTMLUtils.STYLE.listing['properties']['property']})
		try:
			html_str += '$NAME : $VALUE' 
		finally:
			html_str += HTMLUtils.rtag('p')
		return html_str
	
	@staticmethod
	def generate_status():
		html_str = HTMLUtils.ltag('span', {'class' : '$STYLE'})
		try:
			html_str += '$VALUE'
		finally:
			html_str += HTMLUtils.rtag('span')
		return html_str
	
	def write(self):
		ListingGenerator.generate_template()
		template = Template(file_to_str(os.path.join(HTMLUtils.TEMPLATE_DIR, ListingGenerator.TEMPLATE_FILE_LISTING)))
		str = template.substitute(TITLE=self.title, PROPERTIES=self.write_properties(), LISTING=self.write_listing())
		return str
		
	def write_properties(self):
		template = Template(file_to_str(os.path.join(HTMLUtils.TEMPLATE_DIR, ListingGenerator.TEMPLATE_FILE_PROPERTY)))
		str = ''
		for name, value in self.properties.items():
			if name.upper() == 'STATUS':
				str += template.substitute(NAME=name, VALUE=self.write_status(value))
			else:
				str += template.substitute(NAME=name, VALUE=value)
		return str

	def write_status(self, value):
		template = Template(file_to_str(os.path.join(HTMLUtils.TEMPLATE_DIR, ListingGenerator.TEMPLATE_FILE_STATUS)))
		return template.substitute(STYLE=HTMLUtils.STYLE.status[value.lower()], VALUE=value)
	
	def write_listing(self):
		str = ''
		for generator in self.generators:
			str += generator.write()
		return str
		