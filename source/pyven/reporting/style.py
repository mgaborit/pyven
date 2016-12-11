class Style(object):
	
	def __init__(self, template='pyven/reporting/style_template.css'):
		self.template = template
		self.status = {'success' : 'success', 'failure' : 'failure', 'unknown' : 'unknown'}
		self.step = {'div' : 'stepDiv', 'properties' : {'div' : 'propertiesDiv', 'property' : 'property'}}
		self.error = {'div' : 'errorDiv', 'error' : 'error'}
		self.warning = {'div' : 'warningDiv', 'warning' : 'warning'}
		
	def write(self):
		css = """
			<!--/* <![CDATA[ */
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
		css += '.' + self.step['div'] + """
			{
				margin : 3px 25px;
				padding-left : 25px;
				padding-bottom : 5px;
				padding-top : 5px;
				border : 1px solid #d9d9d9;
			}
		"""
		css += '.' + self.step['properties']['div'] + """
			{
				margin-bottom : 15px;
				padding-left : 10px;
			}
		"""
		css += '.' + self.step['properties']['property'] + """
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
		css += """
			/* ]]> */-->
		"""
		return css