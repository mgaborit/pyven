from pyven.reporting.content.status import Status
from pyven.reporting.style import Style
import pyven.constants

class Success(Status):

	def __init__(self):
		super(Success, self).__init__(pyven.constants.STATUS[0])
		self.status_style = Style.get().status['success']
		