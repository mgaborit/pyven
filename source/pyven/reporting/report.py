import os, webbrowser, logging, codecs

from pyven.exceptions.exception import PyvenException
from pyven.pyven import Pyven

from pyven.reporting.style import Style

import pyven.constants

logger = logging.getLogger('global')

class Report(object):
	
	def __init__(self, pyven, nb_lines=10, index='index.html', platform_report=pyven.constants.PLATFORM+'.html'):
		self.pyven = pyven
		self.nb_lines = nb_lines
		self.platform_report = platform_report
		self.index = index
		self.style = Style()
	
	def _write_error(self, error):
		html_str = '<div class="' + self.style.error['div'] + '">'
		html_str += '<span class="' + self.style.error['error'] + '"><p>' + '</p><p>'.join(error) + '</p></span>'
		html_str += '</div>'
		return html_str
	
	def _write_warning(self, warning):
		html_str = '<div class="' + self.style.warning['div'] + '">'
		html_str += '<span class="' + self.style.warning['warning'] + '"><p>' + '</p><p>'.join(warning) + '</p></span>'
		html_str += '</div>'
		return html_str
	
	def _write_head(self):
		html_str = '<html xmlns="http://www.w3.org/1999/xhtml" lang="fr-FR" xml:lang="fr-FR">'
		html_str += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		html_str += "<title>Build report</title>"
		html_str += '<style type="text/css">'
		html_str += self.style.write()
		html_str += '</style>'
		html_str += '</head>'
		return html_str
		
	def _write_step(self, step):
		html_str = '<a name="' + pyven.constants.PLATFORM + '_' + '_'.join(step.report_identifiers()) + '"><div class="stepDiv">'
		try:
			html_str += '<h2>' + ' '.join(step.report_identifiers()) + '</h2>'
			html_str += '<div class="' + self.style.step['properties']['div'] + '">'
			if step.report_status() == 'SUCCESS':
				status_style = self.style.status['success']
			elif step.report_status() == 'FAILURE':
				status_style = self.style.status['failure']
			else:
				status_style = self.style.status['unknown']
			html_str += '<p class="' + self.style.step['properties']['property'] + '">Status : <span class="' + status_style + '">' + step.report_status() + '</span></p>'
			for property in step.report_properties():
				html_str += '<p class="' + self.style.step['properties']['property'] + '">' + property[0] + ' : ' + property[1] + '</p>'
			html_str += '</div>'
			displayed_errors = 0
			nb_errors = 0
			for error in step.errors:
				if displayed_errors < self.nb_lines:
					html_str += self._write_error(error)
					displayed_errors += 1
				nb_errors += 1
			if nb_errors > displayed_errors:
				html_str += self._write_error([str(nb_errors - displayed_errors) + ' more errors...'])
			displayed_warnings = 0
			nb_warnings = 0
			for warning in step.warnings:
				if displayed_warnings < self.nb_lines - displayed_errors:
					html_str += self._write_warning(warning)
					displayed_warnings += 1
				nb_warnings += 1
			if nb_warnings > displayed_warnings:
				html_str += self._write_warning([str(nb_warnings - displayed_warnings) + ' more warnings...'])
		finally:
			html_str += '</div></a>'
		return html_str
		
	def _write_body(self):
		html_str = self._write_summary()
		for step in self.pyven.reportables():
			html_str += self._write_step(step)
		return html_str
	
	def _write_summary(self):
		html_str = ''
		html_str += '<div class="' + self.style.step['div'] + '">'
		html_str += '<h2>Summary</h2>'
		status = 'SUCCESS'
		for step in self.pyven.reportables():
			if step.report_status() != 'SUCCESS':
				status = 'FAILURE'
		if status == 'FAILURE':
			for step in self.pyven.reportables():
				if step.report_status() != 'SUCCESS':
					html_str += self._write_error([' '.join(step.report_summary()) + ' <a href="#' + pyven.constants.PLATFORM + '_' + '_'.join(step.report_identifiers()) + '">Details</a>'])
		else:
			html_str += '<span class="' + self.style.status['success'] + '">SUCCESS</span>'
		html_str += '</div>'
		return html_str
	
	def write(self):
		html_str = self._write_body()
		report_dir = os.path.join(Pyven.WORKSPACE.url, 'report')
		if not os.path.isdir(report_dir):
			os.makedirs(report_dir)
		html_file = codecs.open(os.path.join(report_dir, self.platform_report), 'w', 'utf-8')
		html_file.write(html_str)
		html_file.close()
	
	def aggregate(self):
		logger.info('Aggregating build reports')
		report_dir = os.path.join(Pyven.WORKSPACE.url, 'report')
		if os.path.isdir(report_dir):
			html_str = '<html>'
			html_str += self._write_head()
			html_str += '<body>'
			html_str += '<h1>Build report</h1>'
			for fragment in os.listdir(report_dir):
				if os.path.splitext(fragment)[1] == '.html' and os.path.splitext(fragment)[0] != 'index':
					html_str += '<div class="' + self.style.step['div'] + '">'
					html_str += '<h2>'+os.path.splitext(fragment)[0]+'</h2>'
					f = codecs.open(os.path.join(report_dir, fragment), 'r', 'utf-8')
					html_str += f.read()
					f.close()
					html_str += '</div>'
					logger.info(os.path.splitext(fragment)[0]+' report added')
			html_str += '</body>'
			html_str += '</html>'
			
			html_file = codecs.open(os.path.join(report_dir, self.index), 'w', 'utf-8')
			html_file.write(html_str)
			html_file.close()
			logger.info('Report generated')
	
	def display(self):
		webbrowser.open_new_tab(os.path.join(Pyven.WORKSPACE.url, 'report', self.index))
		