import os
from pyven.utils.utils import str_to_file, file_to_str

class Style(object):
	DIR = os.path.join(os.environ.get('PVN_HOME'), 'report', 'css')
	COUNT = 0
	SINGLETON = None
	
	def __init__(self, name='default'):
		Style.COUNT += 1
		self.name = name
		self.go_top = 'goTop'
		
		self.line = {'div_style' : 'lineDiv', 'span_style' : 'lineSpan', 'part_style' : 'linePart'}
		self.error = {'div_style' : 'errorDiv', 'span_style' : 'errorSpan'}
		self.warning = {'div_style' : 'warningDiv', 'span_style' : 'warningSpan'}
		self.lines = {'div_style' : 'linesDiv'}
		self.status = {'div_style' : 'statusDiv', 'span_style' : 'statusSpan'}
		self.failure = {'span_style' : 'failureSpan'}
		self.success = {'span_style' : 'successSpan'}
		self.title = {'title_style' : 'titleH2'}
		self.property = {'p_style' : 'propertyP'}
		self.properties = {'div_style' : 'propertiesDiv'}
		self.listing = {'div_style' : 'listingDiv'}
		
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
		css = '.' + self.go_top + """
			{
				float: right;
				clear: none;
				font-size : 16px;
				font-weight : bold;
				font-family: Arial;
				padding-right : 5px;
				padding-top : 5px;
			}
		"""
		
		css += 'h1' + """
			{
				font-size : 32px;
				color : #4d4d4d;
				font-weight : bold;
				font-family: Arial;
			}
		"""
		css += 'h2' + """
			{
				font-size : 18px;
				color : #0047b3;
				font-weight : bold;
				font-family: Arial;
			}
		"""
		css += '.' + self.listing['div'] + """
			{
				margin : 3px 25px;
				padding-left : 25px;
				padding-bottom : 5px;
				padding-top : 5px;
				border : 1px solid #d9d9d9;
			}
		"""
		css += '.' + self.listing['properties']['div'] + """
			{
				margin-bottom : 15px;
				padding-left : 10px;
			}
		"""
		css += '.' + self.listing['properties']['property'] + """
			{
				margin : 2px;
				font-size : 16px;
				color : #66a3ff;
				font-family: Arial;
			}
		"""
		css += '.' + self.status['success'] + """
			{
				font-size : 16px;
				color : #00b33c;
				font-family: Arial;
				font-weight : bold;
			}
		"""
		css += '.' + self.status['failure'] + """
			{
				font-size : 16px;
				color : #990000;
				font-family: Arial;
				font-weight : bold;
			}
		"""
		css += '.' + self.status['unknown'] + """
			{
				font-size : 16px;
				color : #666666;
				font-family: Arial;
				font-weight : bold;
			}
		"""
		css += '.' + self.error['error'] + """
			{
				font-size : 14px;
				color : #990000;
				font-family: Arial;
			}
		"""
		css += '.' + self.error['div'] + """
			{
				margin-bottom : 2px;
				margin-left : 20px;
				margin-right : 20px;
				padding : 4px;
				border-width : 1px;
				border-style : dotted;
				border-color : #ffcccc;
			}
		"""
		css += '.' + self.warning['warning'] + """
			{
				font-size : 14px;
				color : #cc4400;
				font-family: Arial;
			}
		"""
		css += '.' + self.warning['div'] + """
			{
				margin-bottom : 2px;
				margin-left : 20px;
				margin-right : 20px;
				padding : 4px;
				border-width : 1px;
				border-style : dotted;
				border-color : #ffc299;
			}
		"""
		return css