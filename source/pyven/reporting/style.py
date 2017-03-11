import os
from pyven.utils.utils import str_to_file, file_to_str

class Style(object):
	DIR = os.path.join(os.environ.get('PVN_HOME'), 'style')
	
	def __init__(self, name='default'):
		self.name = name
		self.status = {'success' : 'success', 'failure' : 'failure', 'unknown' : 'unknown'}
		self.listing = {'div' : 'listingDiv', 'properties' : {'div' : 'propertiesDiv', 'property' : 'property'}}
		self.error = {'div' : 'errorDiv', 'error' : 'error'}
		self.warning = {'div' : 'warningDiv', 'warning' : 'warning'}
		self.go_top = 'goTop'
		
	def inline_inserter(function):
		def _intern(self):
			str = """
				<!--/* <![CDATA[ */
				"""
			try:
				str += function(self)
			finally:
				str += """
					/* ]]> */-->
				"""
			return str
		return _intern
		
	@inline_inserter
	def write(self):
		if not os.path.isdir(Style.DIR):
			os.makedirs(Style.DIR)
		if not os.path.isfile(os.path.join(Style.DIR, self.name)):
			self.name = 'default'
			self.generate_default()
			return self.default()
		else:
			return file_to_str(os.path.join(os.environ.get('PVN_HOME'), 'style', self.name + '.css'))
	
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