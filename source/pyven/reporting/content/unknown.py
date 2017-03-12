from pyven.reporting.content.status import Status
from pyven.reporting.style import Style
import pyven.constants

class Unknown(Status):

	def __init__(self):
		super(Unknown, self).__init__(pyven.constants.STATUS[2])
		self.status_style = Style.get().status['unknown']
		