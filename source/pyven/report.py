import os, webbrowser
from pyven.exception import PyvenException

class Report(object):
	
	def __init__(self, status, index='index.html'):
		self.index = index
		self.html_str = ''
		self.steps = []
		self.status = status
		self.summary = ''
	
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
				font-size : 18px;
				color : #0047b3;
				font-weight : bold;
				font-family: Arial;
			}
			.stepDiv {
				margin : 3px 25px;
				padding-left : 25px;
				padding-bottom : 5px;
				padding-top : 5px;
				border : 1px solid #d9d9d9;
			}
			.propertiesDiv {
				margin-bottom : 15px;
				padding-left : 10px;
			}
			.property {
				margin : 2px;
				font-size : 16px;
				color : #66a3ff;
				font-family: Arial;
			}
			.success {
				font-size : 16px;
				color : #00b33c;
				font-family: Arial;
				font-weight : bold;
			}
			.failure {
				font-size : 16px;
				color : #990000;
				font-family: Arial;
				font-weight : bold;
			}
			.error {
				font-size : 14px;
				color : #990000;
				font-family: Arial;
			}
			.summaryDiv {
				margin-bottom : 2px;
				margin-left : 20px;
				margin-right : 20px;
				padding : 4px;
			}
			.summaryStepDiv {
				margin-bottom : 15px;
				padding-left : 10px;
			}
			.summaryStep {
				margin : 2px;
				font-size : 16px;
				color : #66a3ff;
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
				font-size : 14px;
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
		self.html_str = '<html xmlns="http://www.w3.org/1999/xhtml" lang="fr-FR" xml:lang="fr-FR">'
		self.html_str += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		self.html_str += "<title>Pyven build report</title>"
		self.html_str += '<style type="text/css">'
		self.html_str += self._write_style()
		self.html_str += '</style>'
		self.html_str += '</head>'
		return self.html_str
		
	def _write_body(self):
		self.html_str = '<body>'
		self.html_str += '<h1>Build report</h1>'
		self.html_str += self.summary
		for step in self.steps:
			self.html_str += step
		self.html_str += '</body>'
		return self.html_str
	
	def prepare_summary(self, preprocessors, builders, unit=[], integration=[]):
		self.html_str = ''
		self.html_str += '<div class="stepDiv">'
		self.html_str += '<h2>Summary</h2>'
		self.html_str += '<div class="summaryDiv">'
		if self.status == 'FAILURE':
			self.html_str += '<div class="summaryStepDiv">'
			self.html_str += '<p class="summaryStep">Build :</p>'
			for tool in preprocessors:
				if tool.status() == 'FAILURE':
					self.html_str += tool.report_error(tool.report_summary_description() + ' <a href="#' + tool.report_id() + '">Details</a>')
			for tool in builders:
				if tool.status() == 'FAILURE':
					self.html_str += tool.report_error(tool.report_summary_description() + ' <a href="#' + tool.report_id() + '">Details</a>')
			if len(unit) > 0:
				self.html_str += '<p class="summaryStep">Unit tests :</p>'
				for test in unit:
					if test.status() == 'FAILURE':
						self.html_str += test.report_error(tool.report_summary_description() + ' <a href="#' + test.report_id() + '">Details</a>')
			if len(integration) > 0:
				self.html_str += '<p class="summaryStep">Integration tests :</p>'
				for test in integration:
					if test.status() == 'FAILURE':
						self.html_str += test.report_error(tool.report_summary_description() + ' <a href="#' + test.report_id() + '">Details</a>')
			self.html_str += '</div>'
		else:
			self.html_str += '<span class="success">SUCCESS</span>'
		self.html_str += '</div>'
		self.html_str += '</div>'
		self.summary = self.html_str
	
	def write(self, workspace):
		self.html_str = '<html>'
		self.html_str += self._write_head()
		self.html_str += self._write_body()
		self.html_str += '</html>'
		
		report_dir = os.path.join(workspace, 'report')
		if not os.path.isdir(report_dir):
			os.makedirs(report_dir)
		html_file= open(os.path.join(report_dir, self.index),"w")
		html_file.write(self.html_str)
		html_file.close()
		
	def add_step(self, step):
		self.steps.append(step)
		
	def display(self, workspace):
		webbrowser.open_new_tab(os.path.join(workspace, 'report', self.index))
		