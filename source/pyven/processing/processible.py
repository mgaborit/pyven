import subprocess, time

class Processible(object):
	
	STATUS = {'default' : 'UNKNOWN', 'success' : 'SUCCESS', 'failure' : 'FAILURE'}
	
	def __init__(self):
		self.status = Processible.STATUS['default']
		self.duration = 0
	
	def process(self, mode, verbose=False, warning_as_error=False):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "process"')
	
	def status(self):
		raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "status"')

	def _call_command(self, command):
		tic = time.time()
		sp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
		out, err = sp.communicate()
		toc = time.time()
		return round(toc - tic, 3), out, err, sp.returncode