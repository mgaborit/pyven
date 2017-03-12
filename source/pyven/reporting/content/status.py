import os
from string import Template

from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.utils import str_to_file, file_to_str
from pyven.reporting.content.content import Content
from pyven.reporting.style import Style

class Status(Content):
	TEMPLATE = os.path.join(Content.TEMPLATE_DIR, 'status-template.html')

	def __init__(self, status):
		super(Status, self).__init__()
		self.status = status
		self.div_style = Style.get().status['div_style']
		self.span_style = Style.get().status['span_style']
		self.status_style = ''
		
	def write(self):
		Status.generate_template()
		return self.write_status()
	
	def write_status(self):
		template = Template(file_to_str(Status.TEMPLATE))
		result = template.substitute(VALUE=self.status,\
									DIV_STYLE=' '.join([self.div_style, self.status.lower()]),\
									SPAN_STYLE=' '.join([self.span_style, self.status.lower()]))
		return result
	
	@staticmethod
	def generate_template():
		if not os.path.isdir(Content.TEMPLATE_DIR):
			os.makedirs(Content.TEMPLATE_DIR)
		if not os.path.isfile(Status.TEMPLATE):
			str_to_file(Status.generate_template_status(), Status.TEMPLATE)
	
	@staticmethod
	def generate_template_status():
		html_str = HTMLUtils.ltag('div', {'class' : '$DIV_STYLE'})
		try:
			html_str += HTMLUtils.ltag('span', {'class' : '$SPAN_STYLE'})
			try:
				html_str += '$VALUE'
			finally:
				html_str += HTMLUtils.rtag('span')
		finally:
			html_str += HTMLUtils.rtag('div')
		return html_str
