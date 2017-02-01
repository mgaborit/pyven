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
		html_str = '<head>'
		html_str += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		html_str += '<title>Build report</title>'
		html_str += '<style type="text/css">'
		html_str += self.style.write()
		html_str += '</style>'
		html_str += '</head>'
		return html_str
		
	def _write_ref(self, idx):
		return pyven.constants.PLATFORM + '_' + str(idx)

	def _write_step(self, step, idx):
		html_str = '<a name="' + self._write_ref(idx) + '"><div class="stepDiv">'
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
		count = 0
		for step in self.pyven.reportables():
			html_str += self._write_step(step, count)
			count += 1
		return html_str

	def _write_summary(self):
		html_str = '<div class="' + self.style.step['div'] + '">'
		html_str += '<h2>Summary</h2>'
		status = 'SUCCESS'
		for step in self.pyven.reportables():
			if step.report_status() != 'SUCCESS':
				status = 'FAILURE'
		if status == 'FAILURE':
			count = 0
			for step in self.pyven.reportables():
				if step.report_status() != 'SUCCESS':
					html_str += self._write_error([' '.join(step.report_summary()) + ' <a href="#' + self._write_ref(count) + '">Details</a>'])
				count += 1
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
	
	def _write_platforms(self, platforms):
		html_str = '<div class="' + self.style.step['div'] + '">'
		html_str += '<h2>Platforms</h2>'
		html_str += '<div class="' + self.style.step['properties']['div'] + '">'
		for platform in platforms:
			html_str += '<p class="' + self.style.step['properties']['property'] + '"><a href="#' + platform + '">' + platform + '</a></p>'
		html_str += '</div></div>'
		return html_str
	
	def aggregate(self):
		logger.info('Aggregating build reports')
		report_dir = os.path.join(Pyven.WORKSPACE.url, 'report')
		if os.path.isdir(report_dir):
			html_str = '<html xmlns="http://www.w3.org/1999/xhtml" lang="en-EN" xml:lang="en-EN">'
			html_str += self._write_head()
			html_str += '<body>'
			html_str += '<h1>Build report</h1>'
			platforms = [os.path.splitext(p)[0] for p in os.listdir(report_dir) if os.path.splitext(p)[1] == '.html' and os.path.splitext(p)[0] != 'index']
			html_str += self._write_platforms(platforms)
			for fragment in os.listdir(report_dir):
				if os.path.splitext(fragment)[1] == '.html' and os.path.splitext(fragment)[0] != 'index':
					html_str += '<a name="' + os.path.splitext(fragment)[0] + '">'
					html_str += '<div class="' + self.style.step['div'] + '">'
					html_str += '<h2>'+os.path.splitext(fragment)[0]+'</h2>'
					f = codecs.open(os.path.join(report_dir, fragment), 'r', 'utf-8')
					html_str += f.read()
					f.close()
					html_str += '</div></a>'
					logger.info(os.path.splitext(fragment)[0]+' report added')
			html_str += '</body>'
			html_str += '</html>'
			
			html_file = codecs.open(os.path.join(report_dir, self.index), 'w', 'utf-8')
			html_file.write(html_str)
			html_file.close()
			logger.info('Report generated')
	
	def display(self):
		webbrowser.open_new_tab(os.path.join(Pyven.WORKSPACE.url, 'report', self.index))
		