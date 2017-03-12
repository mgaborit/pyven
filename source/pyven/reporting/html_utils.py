import os, webbrowser, shutil
from string import Template

from pyven.exceptions.exception import PyvenException

from pyven.reporting.style import Style

import pyven.constants
from pyven.logging.logger import Logger
from pyven.utils.utils import str_to_file, file_to_str

class HTMLUtils(object):
	INDEX = 'index.html'
	TEMPLATE_DIR = os.path.join(os.environ.get('PVN_HOME'), 'report', 'html')
	TEMPLATE_FILE = 'index-template.html'
	
	def __init__(self, nb_lines=10):
		self.nb_lines = nb_lines
		
	@staticmethod
	def set_style(style):
		Style.get().name = style
			
	@staticmethod
	def ltag(name, attributes={}):
		tag = '<' + name
		if len(attributes) > 0:
			tag += ' '
		return tag + ' '.join([k + '="' + v + '"' for k, v in attributes.items()]) + '>'
	
	@staticmethod
	def rtag(name):
		return '</' + name + '>'
	
	@staticmethod
	def link(str, ref):
		html_str = HTMLUtils.ltag('a', {'href' : '#'+ref})
		try:
			html_str += str
		finally:
			html_str += HTMLUtils.rtag('a')
		return html_str
		
	@staticmethod
	def target(str, ref):
		html_str = HTMLUtils.ltag('a', {'name' : ref})
		try:
			html_str += str
		finally:
			html_str += HTMLUtils.rtag('a')
		return html_str
		
	@staticmethod
	def write(html_str, workspace, step):
		report_dir = os.path.join(workspace, 'report')
		if not os.path.isdir(report_dir):
			os.makedirs(report_dir)
		str_to_file(html_str, os.path.join(report_dir, pyven.constants.PLATFORM + '-' + step + '.html'))

	@staticmethod
	def aggregate(workspace):
		report_dir = os.path.join(workspace, 'report')
		if not os.path.isdir(report_dir):
			os.makedirs(report_dir)
		template_file = os.path.join(HTMLUtils.TEMPLATE_DIR, HTMLUtils.TEMPLATE_FILE) 
		if not os.path.isfile(template_file):
			HTMLUtils.generate_template()
		template = Template(file_to_str(template_file))
		str = template.substitute(STYLE=Style.get().write(), CONTENT=HTMLUtils.write_body(workspace))
		str_to_file(str, os.path.join(report_dir, HTMLUtils.INDEX))
	
	@staticmethod
	def display(workspace):
		webbrowser.open_new_tab(os.path.join(workspace, 'report', HTMLUtils.INDEX))
		
	@staticmethod
	def clean(workspace):
		report_dir = os.path.join(workspace, 'report')
		if os.path.isdir(report_dir):
			shutil.rmtree(report_dir)
	
	# def _write_ref(self, idx, path):
		# return HTMLUtils._path_to_report_name(path) + '_' + str(idx)

	# def _write_reportable(self, reportable, idx):
		# html_str = '<a name="' + self._write_ref(idx, '_'.join(reportable.report_summary())) + '"><div class="stepDiv">'
		# try:
			# html_str += '<h2>' + ' '.join(reportable.report_identifiers()) + '</h2>'
			# html_str += '<div class="' + Style.get().reportable['properties']['div'] + '">'
			# if reportable.report_status() == 'SUCCESS':
				# status_style = Style.get().status['success']
			# elif reportable.report_status() == 'FAILURE':
				# status_style = Style.get().status['failure']
			# else:
				# status_style = Style.get().status['unknown']
			# html_str += '<p class="' + Style.get().reportable['properties']['property'] + '">Status : <span class="' + status_style + '">' + reportable.report_status() + '</span></p>'
			# for property in reportable.report_properties():
				# html_str += '<p class="' + Style.get().reportable['properties']['property'] + '">' + property[0] + ' : ' + property[1] + '</p>'
			# html_str += '</div>'
			# displayed_errors = 0
			# nb_errors = 0
			# for error in reportable.errors:
				# if displayed_errors < self.nb_lines:
					# html_str += self._write_error(error)
					# displayed_errors += 1
				# nb_errors += 1
			# if nb_errors > displayed_errors:
				# html_str += self._write_error([str(nb_errors - displayed_errors) + ' more errors...'])
			# displayed_warnings = 0
			# nb_warnings = 0
			# for warning in reportable.warnings:
				# if displayed_warnings < self.nb_lines - displayed_errors:
					# html_str += self._write_warning(warning)
					# displayed_warnings += 1
				# nb_warnings += 1
			# if nb_warnings > displayed_warnings:
				# html_str += self._write_warning([str(nb_warnings - displayed_warnings) + ' more warnings...'])
		# finally:
			# html_str += '</div></a>'
		# return html_str
		
	# def _write_summary(self):
		# html_str = '<div class="' + Style.get().step['div'] + '">'
		# html_str += '<h2>Summary</h2>'
		# status = 'SUCCESS'
		# for step in self.pyven.reportables():
			# if step.report_status() != 'SUCCESS':
				# status = 'FAILURE'
		# if status == 'FAILURE':
			# count = 0
			# for step in self.pyven.reportables():
				# if step.report_status() != 'SUCCESS':
					# html_str += self._write_error([' '.join(step.report_summary()) + ' <a href="#' + self._write_ref(count, '_'.join(step.report_summary())) + '">Details</a>'])
				# count += 1
		# else:
			# html_str += '<span class="' + Style.get().status['success'] + '">SUCCESS</span>'
		# html_str += '</div>'
		# return html_str
	
	# @staticmethod
	# def _write_projects(projects):
		# html_str = '<div class="' + Style.get().step['div'] + '">'
		# html_str += '<h2>Pyven projects</h2>'
		# html_str += '<div class="' + Style.get().step['properties']['div'] + '">'
		# for project in projects:
			# html_str += '<p class="' + Style.get().step['properties']['property'] + '"><a href="#' + project + '">' + HTMLUtils._report_name_to_path(project) + '</a></p>'
		# html_str += '</div></div>'
		# return html_str
	
	@staticmethod
	def write_body(workspace):
		report_dir = os.path.join(workspace, 'report')
		html_str = ''
		if os.path.isdir(report_dir):
			report_parts = [f for f in os.listdir(report_dir) if os.path.splitext(f)[1] == '.html' and f != HTMLUtils.INDEX]
			for report_part in report_parts:
				html_str += file_to_str(os.path.join(report_dir, report_part))
		return html_str
	
	@staticmethod
	def generate_template():
		template_dir = HTMLUtils.TEMPLATE_DIR
		if not os.path.isdir(template_dir):
			os.makedirs(template_dir)
		str_to_file(HTMLUtils.generate_html(), os.path.join(template_dir, HTMLUtils.TEMPLATE_FILE))
	
	@staticmethod
	def generate_html():
		html_str = HTMLUtils.ltag('html', {'xmlns' : 'http://www.w3.org/1999/xhtml', 'lang' : 'en-EN', 'xml:lang' : 'en-EN'})
		try:
			html_str += HTMLUtils.generate_head()
			html_str += HTMLUtils.generate_body()
		finally:
			html_str += HTMLUtils.rtag('html')
		return html_str

	@staticmethod
	def generate_head():
		html_str = HTMLUtils.ltag('head')
		try:
			html_str += HTMLUtils.ltag('meta', {'http-equiv' : 'Content-Type', 'content' : 'text/html; charset=utf-8'})
			html_str += HTMLUtils.ltag('title')
			try:
				html_str += 'Pyven build report'
			finally:
				html_str += HTMLUtils.rtag('title')
			html_str += HTMLUtils.ltag('style', {'type' : 'text/css'})
			try:
				html_str += '$STYLE'
			finally:
				html_str += HTMLUtils.rtag('style')
		finally:
			html_str += HTMLUtils.rtag('head')
		return html_str

	@staticmethod
	def generate_body():
		html_str = HTMLUtils.ltag('body')
		try:
			html_str += HTMLUtils.ltag('h1')
			try:
				html_str += 'Build report'
			finally:
				html_str += HTMLUtils.rtag('h1')
			html_str += '$CONTENT'
		finally:
			html_str += HTMLUtils.rtag('body')
		return html_str
