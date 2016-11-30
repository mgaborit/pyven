import os, webbrowser
from pyven.exception import PyvenException

class StepReport(object):
	
	def __init__(self, name):
		self.name = name
		self.errors = []
		self.warnings = []
		
	def add_error(self, str):
		self.errors.append(str)
		
	def add_warning(self, str):
		self.warnings.append(str)
	
	def _write_error(self, error):
		html_str = '<div class="errorDiv">'
		html_str += '<span class="error">' + error + '</span>'
		html_str += '</div>'
		return html_str
	
	def _write_warning(self, warning):
		html_str = '<div class="warningDiv">'
		html_str += '<span class="warning">' + warning + '</span>'
		html_str += '</div>'
		return html_str
	
	def write(self):
		html_str = '<div class="stepDiv">'
		html_str += '<h2>' + self.name + '</h2>'
		for error in self.errors:
			html_str += self._write_error(error)
		for warning in self.warnings:
			html_str += self._write_warning(warning)
		html_str += '</div>'
		return html_str
		
	def parse_errors(self, logs, error_tokens):
		for line in logs:
			i = 0
			found = False
			while not found and i < len(error_tokens):
				if error_tokens[i] in line:
					self.add_error(line)
					found = True
				else:
					i += 1
			
	def parse_warnings(self, logs, warning_tokens):
		for line in logs:
			i = 0
			found = False
			while not found and i < len(warning_tokens):
				if warning_tokens[i] in line:
					self.add_warning(line)
					found = True
				else:
					i += 1
				
class Report(object):
	
	def __init__(self):
		self.index = 'index.html'
		self.steps = []
	
	def _write_style(self):
		css_str = """
			<!--/* <![CDATA[ */

			h1 {
				font-size : 32px;
				color : #4d4d4d;
				font-weight : bold;
				font-family: Arial;
			}
			
			h2 {
				font-size : 20px;
				color : #0047b3;
				font-weight : bold;
				font-family: Arial;
			}
			.stepDiv {
				margin : 3px 25px;
				padding-left : 25px;
				padding-bottom : 25px;
				border : 1px solid #d9d9d9;
			}
			.error {
				font-size : 16px;
				color : #990000;
				font-family: Arial;
			}
			.errorDiv {
				margin-bottom : 2px;
				margin-left : 20px;
				margin-right : 20px;
				padding : 4px;
				border-width : 1px;
				border-style : dotted;
				border-color : #ffcccc;
			}
			.warning {
				font-size : 16px;
				color : #cc4400;
				font-family: Arial;
			}
			.warningDiv {
				margin-bottom : 2px;
				margin-left : 20px;
				margin-right : 20px;
				padding : 4px;
				border-width : 1px;
				border-style : dotted;
				border-color : #ffc299;
			}
			
			/* ]]> */-->
		"""
		return css_str
	
	def _write_head(self):
		html_str = '<html xmlns="http://www.w3.org/1999/xhtml" lang="fr-FR" xml:lang="fr-FR">'
		html_str += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		html_str += "<title>Pyven build report</title>"
		html_str += '<style type="text/css">'
		html_str += self._write_style()
		html_str += '</style>'
		html_str += '</head>'
		return html_str
		
	def _write_body(self):
		html_str = '<body>'
		html_str += '<h1>Pyven build report</h1>'
		for step in self.steps:
			html_str += step.write()
		html_str += '</body>'
		return html_str
	
	def write(self, workspace):
		html_str = '<html>'
		html_str += self._write_head()
		html_str += self._write_body()
		html_str += '</html>'
		
		report_dir = os.path.join(workspace, 'report')
		if not os.path.isdir(report_dir):
			os.makedirs(report_dir)
		html_file= open(os.path.join(report_dir, self.index),"w")
		html_file.write(html_str)
		html_file.close()
		
	def add_step(self, step):
		self.steps.append(step)
		
	def display(self, workspace):
		webbrowser.open_new_tab(os.path.join(workspace, 'report', self.index))
		