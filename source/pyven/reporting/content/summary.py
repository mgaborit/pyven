import os
from string import Template

import pyven.constants
from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.utils import file_to_str, str_to_file
from pyven.reporting.style import Style
from pyven.reporting.content.listing import Listing
from pyven.reporting.content.title import Title
from pyven.reporting.content.error import Error
from pyven.reporting.content.lines import Lines

class Summary(Listing):

	def __init__(self, status, listings):
		super(Summary, self).__init__(title=Title('Failures summary'), status=status, properties=None, lines=None, listings=listings)
		self.div_style = Style.get().summary['div_style']

	def write_listing(self):
		template = Template(file_to_str(Listing.TEMPLATE))
		failures = []
		if self.listings is not None:
			for listing in self.listings:
				if listing.status.status == pyven.constants.STATUS[1]:
					failures.append(Error([HTMLUtils.link(listing.title.title, listing.href())]))
		lines = Lines(failures)
		return template.substitute(TITLE=self.title.write(),\
									STATUS='',\
									PROPERTIES='',\
									LINES=lines.write(),\
									LISTINGS='',\
									DIV_STYLE=Listing.join_styles([Style.get().listing['div_style'], self.div_style, self.status_style]))
