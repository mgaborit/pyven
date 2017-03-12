import os
from string import Template

from pyven.reporting.html_utils import HTMLUtils
from pyven.utils.utils import str_to_file, file_to_str
from pyven.reporting.content.content import Content
from pyven.reporting.style import Style

class Title(Content):
	TEMPLATE = os.path.join(Content.TEMPLATE_DIR, 'title-template.html')

	def __init__(self, title):
		super(Title, self).__init__()
		self.title = title
		self.title_style = Style.get().title['title_style']
		
	def write(self):
		Title.generate_template()
		return self.write_title()
	
	def write_title(self):
		template = Template(file_to_str(Title.TEMPLATE))
		result = template.substitute(VALUE=self.title, TITLE_STYLE=self.title_style)
		return result
	
	@staticmethod
	def generate_template():
		if not os.path.isdir(Content.TEMPLATE_DIR):
			os.makedirs(Content.TEMPLATE_DIR)
		if not os.path.isfile(Title.TEMPLATE):
			str_to_file(Title.generate_template_title(), Title.TEMPLATE)
	
	@staticmethod
	def generate_template_title():
		html_str = HTMLUtils.ltag('h2', {'class' : '$TITLE_STYLE'})
		try:
			html_str += '$VALUE'
		finally:
			html_str += HTMLUtils.rtag('h2')
		return html_str
