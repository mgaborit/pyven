import os
from pyven.utils.utils import str_to_file, file_to_str

class Style(object):
	DIR = os.path.join(os.environ.get('PVN_HOME'), 'report', 'css')
	COUNT = 0
	SINGLETON = None
	
	def __init__(self, name='default'):
		Style.COUNT += 1
		self.name = name
		self.line = {'div_style' : 'line',\
					'part_style' : 'linePart',\
					'error' : 'error',\
					'warning' : 'warning'}
		self.lines = {'div_style' : 'lines'}
		self.status = {'div_style' : 'status',\
						'span_style' : 'status',\
						'success' : 'success',\
						'failure' : 'failure',\
						'unknown' : 'unknown'}
		self.title = {'title_style' : 'title'}
		self.property = {'p_style' : 'property'}
		self.properties = {'div_style' : 'properties'}
		self.listing = {'div_style' : 'listing'}
		self.summary = {'div_style' : 'summary'}
		self.platform = {'div_style' : 'platform'}
		self.step = {'div_style' : 'step'}
		self.reportable = {'div_style' : 'reportable'}
		
	@staticmethod
	def get():
		if Style.COUNT == 0 or Style.SINGLETON is None:
			Style.SINGLETON = Style()

		return Style.SINGLETON
		
	def inline_inserter(function):
		def _intern(self):
			str = "<!--/* <![CDATA[ */"
			try:
				str += function(self)
			finally:
				str += "/* ]]> */-->"
			return str
		return _intern
		
	@inline_inserter
	def write(self):
		if not os.path.isdir(Style.DIR):
			os.makedirs(Style.DIR)
		style_file = os.path.join(Style.DIR, self.name + '.css')
		if not os.path.isfile(style_file):
			self.name = 'default'
			self.generate_default()
			return self.default()
		else:
			return file_to_str(style_file)
	
	def generate_default(self):
		if not os.path.isdir(Style.DIR):
			os.makedirs(Style.DIR)
		str_to_file(self.default(), os.path.join(Style.DIR, 'default.css'))
	
	
	def default(self):
		css = 'h1' + """
			{
				font-size : 32px;
				color : #4d4d4d;
				font-weight : bold;
				font-family: Arial;
			}
		"""
		css += 'h2' + """
			{
				font-size : 20px;
				color : #0047b3;
				font-weight : bold;
				font-family: Arial;
			}
		"""
		css += 'a' + """
			{
				font-size : 16px;
				font-family: Arial;
			}
		"""
		css += '.' + self.listing['div_style'] + """
			{
				margin : 3px 25px;
				padding-left : 25px;
				padding-bottom : 5px;
				padding-top : 5px;
				border : 1px solid #d9d9d9;
			}
		"""
		css += '.' + self.properties['div_style'] + """
			{
				margin-bottom : 15px;
				padding-left : 10px;
			}
		"""
		css += '.' + self.property['p_style'] + """
			{
				margin : 2px;
				font-size : 16px;
				color : #66a3ff;
				font-family: Arial;
			}
		"""
		css += '.' + self.status['success'] + """
			{
				color : #00b33c;
			}
		"""
		css += '.' + self.status['failure'] + """
			{
				color : #990000;
			}
		"""
		css += '.' + self.status['unknown'] + """
			{
				color : #666666;
			}
		"""
		css += '.' + self.status['span_style'] + """
			{
				font-size : 16px;
				font-family: Arial;
				font-weight : bold;
			}
		"""
		css += '.' + self.line['error'] + """
			{
				color : #990000;
				border-color : #ffcccc;
			}
		"""
		css += '.' + self.line['warning'] + """
			{
				color : #cc4400;
				border-color : #ffc299;
			}
		"""
		css += '.' + self.line['part_style'] + """
			{
				font-size : 16px;
				font-family: Arial;
			}
		"""
		css += '.' + self.line['div_style'] + """
			{
				margin-bottom : 2px;
				margin-left : 20px;
				margin-right : 20px;
				padding : 4px;
				border-width : 1px;
				border-style : dotted;
			}
		"""
		return css