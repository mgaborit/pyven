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
	def line_separator():
		return HTMLUtils.ltag('div', {'class' : Style.get().line_separator}) + HTMLUtils.rtag('div')
		
		
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
		title = 'Build report'
		if 'BUILD_NUMBER' in os.environ:
			title = 'Jenkins - Build #' + os.environ.get('BUILD_NUMBER')
		str = template.substitute(STYLE=Style.get().write(), TITLE=title, CONTENT=HTMLUtils.write_body(workspace))
		str_to_file(str, os.path.join(report_dir, HTMLUtils.INDEX))
	
	@staticmethod
	def display(workspace):
		webbrowser.open_new_tab(os.path.join(workspace, 'report', HTMLUtils.INDEX))
		
	@staticmethod
	def clean(workspace):
		report_dir = os.path.join(workspace, 'report')
		if os.path.isdir(report_dir):
			shutil.rmtree(report_dir)
	
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
				html_str += '$TITLE'
			finally:
				html_str += HTMLUtils.rtag('h1')
			html_str += '$CONTENT'
		finally:
			html_str += HTMLUtils.rtag('body')
		return html_str
