import os, webbrowser, codecs, shutil

from pyven.exceptions.exception import PyvenException

from pyven.reporting.style import Style

import pyven.constants
from pyven.logging.logger import Logger
from pyven.utils.utils import hash

class HTMLUtils(object):
	INDEX = 'index.html'
	STYLE = Style()
	NB_LINES=10
	
	def __init__(self, nb_lines=10):
		self.nb_lines = nb_lines
		
	@staticmethod
	def ltag(name, attributes={}):
		return '<' + name + ' ' + ' '.join([k + '="' + v + '"' for k, v in attributes.items()]) + '>\n'
	
	@staticmethod
	def rtag(name):
		return '</' + name + '>\n'
	
	@staticmethod
	def error(function):
		def _intern(self, error):
			html_str = HTMLUtils.ltag('div', {'class' : HTMLUtils.STYLE.error['div']})
			try:
				html_str += HTMLUtils.ltag('span', {'class' : HTMLUtils.STYLE.error['error']})
				try:
					for line in function(self, error):
						html_str += HTMLUtils.ltag('p')
						try:
							html_str += line
						finally:
							html_str += HTMLUtils.rtag('p')
				finally:
					html_str += HTMLUtils.rtag('span')
			finally:
				html_str += HTMLUtils.rtag('div')
			return html_str
		return _intern

	@staticmethod
	def warning(function):
		def _intern(self, warning):
			html_str = HTMLUtils.ltag('div', {'class' : HTMLUtils.STYLE.warning['div']})
			try:
				html_str += HTMLUtils.ltag('span', {'class' : HTMLUtils.STYLE.warning['warning']})
				try:
					for line in function(self, warning):
						html_str += HTMLUtils.ltag('p')
						try:
							html_str += line
						finally:
							html_str += HTMLUtils.rtag('p')
				finally:
					html_str += HTMLUtils.rtag('span')
			finally:
				html_str += HTMLUtils.rtag('div')
			return html_str
		return _intern
	
	@staticmethod
	def listing(function):
		def _intern(self):
			html_str = HTMLUtils.ltag('div', {'class' : HTMLUtils.STYLE.listing['div']})
			try:
				html_str += function(self)
			finally:
				html_str += HTMLUtils.rtag('div')
			return html_str
		return _intern
	
	@staticmethod
	def listing_title(function):
		def _intern(self, title):
			html_str = HTMLUtils.ltag('h2')
			try:
				html_str += function(self, title)
			finally:
				html_str += HTMLUtils.rtag('h2')
			return html_str
		return _intern
	
	@staticmethod
	def listing_properties(function):
		def _intern(self):
			html_str = HTMLUtils.ltag('div', {'class' : HTMLUtils.STYLE.listing['properties']['div']})
			try:
				html_str += function(self)
			finally:
				html_str += HTMLUtils.rtag('div')
			return html_str
		return _intern

	@staticmethod
	def listing_property(function):
		def _intern(self, name, value):
			html_str = HTMLUtils.ltag('p', {'class' : HTMLUtils.STYLE.listing['properties']['property']})
			try:
				html_str += function(self, name, value)
			finally:
				html_str += HTMLUtils.rtag('p')
			return html_str
		return _intern
	
	@staticmethod
	def write(html_str, workspace):
		report_dir = os.path.join(workspace, 'report')
		if not os.path.isdir(report_dir):
			os.makedirs(report_dir)
		html_file = codecs.open(os.path.join(report_dir, HTMLUtils.INDEX), 'w', 'utf-8')
		html_file.write(html_str)
		html_file.close()

	@staticmethod
	def clean(workspace):
		report_dir = os.path.join(workspace, 'report')
		if os.path.isdir(report_dir):
			shutil.rmtree(report_dir)
	
	# @div
	# def write_reportable(self, reportable, title, properties):
		# html_str = '<a name="' + self._write_ref(idx, '_'.join(reportable.report_summary())) + '"><div class="stepDiv">'
		# try:
			# html_str += '<h2>' + ' '.join(reportable.report_identifiers()) + '</h2>'
			# html_str += '<div class="' + HTMLUtils.STYLE.reportable['properties']['div'] + '">'
			# if reportable.report_status() == 'SUCCESS':
				# status_style = HTMLUtils.STYLE.status['success']
			# elif reportable.report_status() == 'FAILURE':
				# status_style = HTMLUtils.STYLE.status['failure']
			# else:
				# status_style = HTMLUtils.STYLE.status['unknown']
			# html_str += '<p class="' + HTMLUtils.STYLE.reportable['properties']['property'] + '">Status : <span class="' + status_style + '">' + reportable.report_status() + '</span></p>'
			# for property in reportable.report_properties():
				# html_str += '<p class="' + HTMLUtils.STYLE.reportable['properties']['property'] + '">' + property[0] + ' : ' + property[1] + '</p>'
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
	
	# @staticmethod
	# def _failure_comment():
		# return '<!-- FAILURE -->'
	
	# @staticmethod
	# def _report_name_to_path(name):
		# name_platform = name.split('_PLATFORM_')
		# if name_platform[0].startswith('root_project'):
			# return 'Root project'
		# if name_platform[1] == 'windows':
			# return '\\'.join(name_platform[0].split('_SLASH_'))
		# else:
			# return '/'.join(name_platform[0].split('_SLASH_'))
	
	# @staticmethod
	# def _path_to_report_name(path):
		# return '_SLASH_'.join(path.split(os.sep)) + '_PLATFORM_' + pyven.constants.PLATFORM

	# @staticmethod
	# def _path_to_report_filename(path):
		# return HTMLUtils._path_to_report_name(path) + '.html'
	
	# def _project_report_name(self):
		# name = 'root_project_PLATFORM_' + pyven.constants.PLATFORM + '.html'
		# if self.pyven.path != '':
			# name = self._path_to_report_filename(self.pyven.path)
		# return name

	# def _write_error(self, error):
		# html_str = '<div class="' + HTMLUtils.STYLE.error['div'] + '">'
		# html_str += '<span class="' + HTMLUtils.STYLE.error['error'] + '"><p>' + '</p><p>'.join(error) + '</p></span>'
		# html_str += '</div>'
		# return html_str
	
	# def _write_warning(self, warning):
		# html_str = '<div class="' + HTMLUtils.STYLE.warning['div'] + '">'
		# html_str += '<span class="' + HTMLUtils.STYLE.warning['warning'] + '"><p>' + '</p><p>'.join(warning) + '</p></span>'
		# html_str += '</div>'
		# return html_str
	
	# def _write_head(self):
		# html_str = '<head>'
		# html_str += '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
		# html_str += '<title>Build report</title>'
		# html_str += '<style type="text/css">'
		# html_str += HTMLUtils.STYLE.write()
		# html_str += '</style>'
		# html_str += '</head>'
		# return html_str
		
	# def _write_ref(self, idx, path):
		# return HTMLUtils._path_to_report_name(path) + '_' + str(idx)

	# def _write_reportable(self, reportable, idx):
		# html_str = '<a name="' + self._write_ref(idx, '_'.join(reportable.report_summary())) + '"><div class="stepDiv">'
		# try:
			# html_str += '<h2>' + ' '.join(reportable.report_identifiers()) + '</h2>'
			# html_str += '<div class="' + HTMLUtils.STYLE.reportable['properties']['div'] + '">'
			# if reportable.report_status() == 'SUCCESS':
				# status_style = HTMLUtils.STYLE.status['success']
			# elif reportable.report_status() == 'FAILURE':
				# status_style = HTMLUtils.STYLE.status['failure']
			# else:
				# status_style = HTMLUtils.STYLE.status['unknown']
			# html_str += '<p class="' + HTMLUtils.STYLE.reportable['properties']['property'] + '">Status : <span class="' + status_style + '">' + reportable.report_status() + '</span></p>'
			# for property in reportable.report_properties():
				# html_str += '<p class="' + HTMLUtils.STYLE.reportable['properties']['property'] + '">' + property[0] + ' : ' + property[1] + '</p>'
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
		
	# def _write_body(self):
		# html_str = ''
		# ok = True
		# i = 0
		# while ok and i < len(self.pyven.reportables()):
			# ok = self.pyven.reportables()[i].report_status() == 'SUCCESS'
			# i += 1
		# if not ok:
			# html_str = HTMLUtils._failure_comment()
		# html_str += self._write_summary()
		# count = 0
		# for step in self.pyven.reportables():
			# html_str += self._write_step(step, count)
			# count += 1
		# return html_str

	# def _write_summary(self):
		# html_str = '<div class="' + HTMLUtils.STYLE.step['div'] + '">'
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
			# html_str += '<span class="' + HTMLUtils.STYLE.status['success'] + '">SUCCESS</span>'
		# html_str += '</div>'
		# return html_str
	
	# def write(self):
		# html_str = self._write_body()
		# report_dir = os.path.join(Pyven.WORKSPACE.url, 'report')
		# if not os.path.isdir(report_dir):
			# os.makedirs(report_dir)
		# html_file = codecs.open(os.path.join(report_dir, self._project_report_name()), 'w', 'utf-8')
		# html_file.write(html_str)
		# html_file.close()
	
	# @staticmethod
	# def _write_projects(projects):
		# html_str = '<div class="' + HTMLUtils.STYLE.step['div'] + '">'
		# html_str += '<h2>Pyven projects</h2>'
		# html_str += '<div class="' + HTMLUtils.STYLE.step['properties']['div'] + '">'
		# for project in projects:
			# html_str += '<p class="' + HTMLUtils.STYLE.step['properties']['property'] + '"><a href="#' + project + '">' + HTMLUtils._report_name_to_path(project) + '</a></p>'
		# html_str += '</div></div>'
		# return html_str
	
	@staticmethod
	def aggregate():
		Logger.get().info('Aggregating build reports')
		if Pyven.WORKSPACE is None:
			Pyven._set_workspace()
		report_dir = os.path.join(Pyven.WORKSPACE.url, 'report')
		if os.path.isdir(report_dir):
			html_str = '<html xmlns="http://www.w3.org/1999/xhtml" lang="en-EN" xml:lang="en-EN">'
			html_str += HTMLUtils._write_head()
			html_str += '<body>'
			html_str += '<h1>Build report</h1>'
			tmp = [f for f in os.listdir(report_dir) if os.path.splitext(f)[1] == '.html' and f != HTMLUtils.index]
			fragments = [f for f in tmp if f.startswith('root_project')]
			fragments.extend([f for f in tmp if not f.startswith('root_project')])
			projects = [os.path.splitext(f)[0] for f in fragments]
			html_str += HTMLUtils._write_projects(projects)
			for fragment in fragments:
				html_str += '<a name="' + os.path.splitext(fragment)[0] + '">'
				html_str += '<div class="' + HTMLUtils.STYLE.step['div'] + '">'
				html_str += '<p class="' + HTMLUtils.STYLE.go_top + '"><a href="#">Top</a></p>'
				html_str += '<h2>'+HTMLUtils._report_name_to_path(os.path.splitext(fragment)[0])+'</h2>'
				file = codecs.open(os.path.join(report_dir, fragment), 'r', 'utf-8')
				html_str += file.read()
				file.close()
				html_str += '</div></a>'
				Logger.get().info(os.path.splitext(fragment)[0]+' report added')
			html_str += '</body>'
			html_str += '</html>'
			
			html_file = codecs.open(os.path.join(report_dir, HTMLUtils.index), 'w', 'utf-8')
			html_file.write(html_str)
			html_file.close()
			Logger.get().info('HTMLUtils generated')
	
	@staticmethod
	def display():
		webbrowser.open_new_tab(os.path.join(Pyven.WORKSPACE.url, 'report', HTMLUtils.index))
		