import subprocess, time

class Processible(object):

    def __init__(self, cwd='.'):
        self.duration = 0
        self.cwd = cwd
    
    def process(self, verbose=False, warning_as_error=False):
        raise NotImplementedError('Invalid call to ' + type(self).__name__ + ' abstract method "process"')
    
    def _call_command(self, command):
        tic = time.time()
        sp = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, cwd=self.cwd)
        out, err = sp.communicate(input='\n')
        toc = time.time()
        return round(toc - tic, 3), out, err, sp.returncode