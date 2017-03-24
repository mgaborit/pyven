import os
from string import Template

import pyven.constants
from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.utils import file_to_str, str_to_file
from pyven.reporting.style import Style
from pyven.reporting.content.listing import Listing
from pyven.reporting.content.summary import Summary

class Platform(Listing):

	def __init__(self, title, status, listings):
		super(Platform, self).__init__(title=title, status=status, properties=None, lines=None, listings=listings, summary=None)
		self.div_style = Style.get().platform['div_style']

	def write_listing(self):
		template = Template(file_to_str(Listing.TEMPLATE))
		listings = ''
		if self.listings is not None:
			if self.status.status == pyven.constants.STATUS[1]:
				listings += Summary(self.status, self.listings).write()
			for listing in self.listings:
				listings += HTMLUtils.line_separator()
				listings += listing.write()
		return template.substitute(TITLE=self.title.write(),\
									STATUS=self.status.write(),\
									PROPERTIES='',\
									LINES='',\
									LISTINGS=listings,\
									DIV_STYLE=Listing.join_styles([Style.get().listing['div_style'], self.div_style, self.status_style]))
		
