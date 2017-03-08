import logging, os

from pyven.exceptions.repository_exception import RepositoryException
from pyven.steps.step import Step

logger = logging.getLogger('global')

def retrieve(type, step, items):
	ok = True
	for item in [i for i in items.values() if i.to_retrieve and i.repo]:
		try:
			if not step.repositories[item.repo].is_reachable():
				if Step.WORKSPACE.is_available(item):
					item.file = os.path.join(item.location(Step.WORKSPACE.url), os.listdir(item.location(Step.WORKSPACE.url))[0])
					logger.info(step.log_path() + 'Workspace --> Retrieved ' + type + ' : ' + item.format_name())
				else:
					raise RepositoryException('Repository ' + item.repo + ' not accessible -->  Unable to retrieve ' + type + ' : ' + item.format_name())
			elif not step.repositories[item.repo].is_available(item):
				raise RepositoryException('Repository ' + item.repo + ' --> ' + type + ' ' + item.format_name() + ' not available')
			elif item.repo != Step.WORKSPACE.name:
				step.repositories[item.repo].retrieve(item, Step.WORKSPACE)
				logger.info(step.log_path() + 'Repository ' + item.repo + ' --> Retrieved ' + type + ' : ' + item.format_name())
			else:
				item.file = os.path.join(item.location(Step.WORKSPACE.url), os.listdir(item.location(Step.WORKSPACE.url))[0])
				logger.info(step.log_path() + 'Workspace --> Retrieved ' + type + ' : ' + item.format_name())
		except RepositoryException as e:
			step.checker.errors.append(e.args)
			for msg in e.args:
				logger.error(msg)
			ok = False
	return ok
		