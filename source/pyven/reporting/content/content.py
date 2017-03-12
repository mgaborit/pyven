import os

from pyven.reporting.html_utils import HTMLUtils

class Content(object):
	NB_LINES=10
	TEMPLATE_DIR = os.path.join(os.environ.get('PVN_HOME'), 'report', 'html')

	def __init__(self):
		pass
		
	def write(self):
		raise NotImplementedError
	