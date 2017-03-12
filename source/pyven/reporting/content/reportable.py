import os
from string import Template

from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.utils import file_to_str, str_to_file
from pyven.reporting.style import Style
from pyven.reporting.content.listing import Listing

class ReportableListing(Listing):

	def __init__(self, title, status, properties, lines):
		super(ReportableListing, self).__init__(title, status, properties, lines, listings=None)
		self.div_style = Style.get().reportable['div_style']

	def write_listing(self):
		template = Template(file_to_str(Listing.TEMPLATE))
		properties = ''
		if self.properties is not None:
			properties += self.properties.write()
		lines = ''
		if self.lines is not None:
			lines += self.lines.write()
		return template.substitute(TITLE=self.title.write(),\
									STATUS=self.status.write(),\
									PROPERTIES=properties,\
									LINES=lines,\
									LISTINGS='',\
									DIV_STYLE=self.div_style)
		