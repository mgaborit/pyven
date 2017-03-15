import os

from pyven.exceptions.repository_exception import RepositoryException
from pyven.steps.step import Step

from pyven.logging.logger import Logger

def retrieve(type, project, items, checker):
	ok = True
	for item in [i for i in items.values() if i.to_retrieve and i.repo]:
		try:
			if project.repositories[item.repo].is_reachable():
				if not project.repositories[item.repo].is_available(item):
					raise RepositoryException('Repository ' + item.repo + ' --> ' + type + ' ' + item.format_name() + ' not available')
				elif item.repo == Step.WORKSPACE.name:
					item.file = os.path.join(item.location(Step.WORKSPACE.url), os.listdir(item.location(Step.WORKSPACE.url))[0])
					Logger.get().info('Workspace --> Retrieved ' + type + ' : ' + item.format_name())
				else:
					project.repositories[item.repo].retrieve(item, Step.WORKSPACE)
					Logger.get().info('Repository ' + item.repo + ' --> Retrieved ' + type + ' : ' + item.format_name())
			
			elif Step.WORKSPACE.is_available(item):
				item.file = os.path.join(item.location(Step.WORKSPACE.url), os.listdir(item.location(Step.WORKSPACE.url))[0])
				Logger.get().info('Workspace --> Retrieved ' + type + ' : ' + item.format_name())
			else:
				raise RepositoryException('Repository ' + item.repo + ' unreachable -->  Unable to retrieve ' + type + ' : ' + item.format_name())
		except RepositoryException as e:
			checker.errors.append(e.args)
			for msg in e.args:
				Logger.get().error(msg)
			ok = False
	return ok
		