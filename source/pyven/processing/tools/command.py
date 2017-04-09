import os, subprocess, time
import pyven.constants

from pyven.processing.tools.tool import Tool
from pyven.reporting.content.property import Property
from pyven.results.line_logs_parser import LineLogsParser

from pyven.logging.logger import Logger

class CommandTool(Tool):

    def __init__(self, cwd, type, report, name, scope, command, directory):
        super(CommandTool, self).__init__(cwd, type, report, name, scope)
        self.command = command
        self.directory = directory
        self.cwd = os.path.join(self.cwd, self.directory)
        self.parser = LineLogsParser(error_patterns=['Error', 'error', 'ERROR', 'Erreur', 'erreur', 'ERREUR'],\
                                    error_exceptions=[],\
                                    warning_patterns=['Warning', 'warning', 'WARNING', 'Avertissement', 'avertissement', 'AVERTISSEMENT'],\
                                    warning_exceptions=[])
    
    def title(self):
        if self.report is not None:
            return self.report
        return 'Command line'
        
    def properties(self):
        properties = []
        properties.append(Property(name='Command', value=self.command))
        properties.append(Property(name='Workspace', value=self.directory))
        properties.append(Property(name='Duration', value=str(self.duration) + ' seconds'))
        return properties
    
    def _call_command(self, command):
        tic = time.time()
        sp = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=self.cwd)
        out, err = sp.communicate(input='\n')
        toc = time.time()
        return round(toc - tic, 3), out, err, sp.returncode
        
    def _format_call(self):
        call = self.command.split(' ')
        Logger.get().info(self.command)
        return call
    
    def process(self, verbose=False, warning_as_error=False):
        Logger.get().info('Preprocessing : ' + self.type + ':' + self.name)
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)
        Logger.get().info('Entering directory : ' + self.directory)
        self.duration, out, err, returncode = self._call_command(self._format_call())
        Logger.get().info('Leaving directory : ' + self.directory)
        
        if verbose:
            for line in out.splitlines():
                Logger.get().info('[' + self.type + ']' + line)
            for line in err.splitlines():
                Logger.get().info('[' + self.type + ']' + line)
        
        self.parser.parse(out.splitlines() + err.splitlines())
        self.warnings = self.parser.warnings
        
        if returncode != 0:
            self.status = pyven.constants.STATUS[1]
            self.errors = self.parser.errors
            Logger.get().error('Preprocessing failed : ' + self.type + ':' + self.name)
        else:
            self.status = pyven.constants.STATUS[0]
        return returncode == 0
    
    def clean(self, verbose=False):
        Logger.get().info('Cleaning : ' + self.type + ':' + self.name + ' --> Nothing to be done')
        return True
        