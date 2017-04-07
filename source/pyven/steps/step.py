import os, time
from threading import Thread

from pyven.logging.logger import Logger

import pyven.constants
from pyven.reporting.content.success import Success
from pyven.reporting.content.failure import Failure
from pyven.reporting.content.unknown import Unknown
from pyven.reporting.content.title import Title

from pyven.utils.parallelizer import Parallelizer

from pyven.exceptions.exception import PyvenException

class Step(object):
    LOCAL_REPO = None
    WORKSPACE = None
    PROJECTS = []
    STATUS = pyven.constants.STATUS

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.name = None
        self.checker = None
        self.status = Step.STATUS[2]

    @staticmethod
    def log_delimiter(path=None):
        Logger.get().info('===================================')
    
    def step(function):
        def _intern(self):
            Step.log_delimiter()
            Logger.get().info('STEP ' + self.name.replace('_', ' ').upper() + ' : STARTING')
            ok = function(self)
            if ok:
                self.status = Step.STATUS[0]
                Logger.get().info('STEP ' + self.name.replace('_', ' ').upper() + ' : SUCCESSFUL')
                Step.log_delimiter()
            else:
                self.status = Step.STATUS[1]
                Logger.get().info('STEP ' + self.name.replace('_', ' ').upper() + ' : FAILED')
                Step.log_delimiter()
            return ok
        return _intern
    
    @staticmethod
    def error_checks(function):
        def _intern(self, project):
            ok = True
            Logger.set_format(project)
            try:
                try:
                    if project.path != os.getcwd():
                        if not os.path.isdir(project.path):
                            raise PyvenException('Subproject path does not exist : ' + project.path)
                    tic = time.time()
                    ok = function(self, project)
                    toc = time.time()
                    Logger.get().info('Step time : ' + str(round(toc - tic, 3)) + ' seconds')
                except PyvenException as e:
                    self.checker.errors.append(e.args)
                    ok = False
            finally:
                Logger.set_format()
            return ok
        return _intern
    
    @step
    def _process_parallel(self):
        self.checker.status = Step.STATUS[2]
        threads = []
        for project in Step.PROJECTS:
            threads.append(Thread(target=self._process, args=(project,)))
        parallelizer = Parallelizer(threads, self.nb_threads)
        parallelizer.run()
        return self.status not in Step.STATUS[1:]
    
    @step
    def _process_sequential(self):
        ok = True
        self.checker.status = Step.STATUS[2]
        for project in Step.PROJECTS:
            if not self._process(project):
                ok = False
        return ok
    
    def process(self):
        raise NotImplementedError('Step process method not implemented')
        
    def report_status(self):
        if self.status == pyven.constants.STATUS[0]:
            return Success()
        elif self.status == pyven.constants.STATUS[1]:
            return Failure()
        else:
            return Unknown()
    
    def _process(self, project):
        raise NotImplementedError
        
    def reportables(self):
        raise NotImplementedError
        
    def content(self):
        raise NotImplementedError
        
    def report(self):
        return self.status != Step.STATUS[2]
        
    def title(self):
        return Title(self.name)