import os
from string import Template

from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.utils import file_to_str, str_to_file
from pyven.reporting.style import Style
from pyven.reporting.content.content import Content
from pyven.reporting.content.title import Title

class Listing(Content):
	TEMPLATE = os.path.join(Content.TEMPLATE_DIR, 'listing-template.html')

	def __init__(self, title, status, properties=None, lines=None, listings=None):
		super(Listing, self).__init__()
		self.title = title
		self.status = status
		self.properties = properties
		self.lines = lines
		self.listings = listings
		self.div_style = Style.get().listing['div_style']

	def write(self):
		Listing.generate_template()
		return self.write_listing()
		
	def write_listing(self):
		template = Template(file_to_str(Listing.TEMPLATE))
		properties = ''
		if self.properties is not None:
			properties += self.properties.write()
		lines = ''
		if self.lines is not None:
			lines += self.lines.write()
		listings = ''
		if self.listings is not None:
			for listing in self.listings:
				listings += listing.write()
		return template.substitute(TITLE=self.title.write(),\
									STATUS=self.status.write(),\
									PROPERTIES=properties,\
									LINES=lines,\
									LISTINGS=listings,\
									DIV_STYLE=self.div_style)
		
	@staticmethod
	def generate_template():
		if not os.path.isdir(Content.TEMPLATE_DIR):
			os.makedirs(Content.TEMPLATE_DIR)
		if not os.path.isfile(Listing.TEMPLATE):
			str_to_file(Listing.generate_template_listing(), Listing.TEMPLATE)
	
	@staticmethod
	def generate_template_listing():
		html_str = HTMLUtils.ltag('div', {'class' : '$DIV_STYLE'})
		try:
			html_str += '$TITLE '
			html_str += '$STATUS '
			html_str += '$PROPERTIES '
			html_str += '$LINES '
			html_str += '$LISTINGS'
		finally:
			html_str += HTMLUtils.rtag('div')
		return html_str
	