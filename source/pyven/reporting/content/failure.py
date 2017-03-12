from pyven.reporting.content.status import Status
from pyven.reporting.style import Style
import pyven.constants

class Failure(Status):

	def __init__(self):
		super(Failure, self).__init__(pyven.constants.STATUS[1])
		self.span_style = Style.get().failure['span_style']
		