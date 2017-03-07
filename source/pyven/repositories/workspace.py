import os, logging, shutil

from pyven.exceptions.repository_exception import RepositoryException

from pyven.repositories.directory import DirectoryRepo

logger = logging.getLogger('global')

class Workspace(DirectoryRepo):

	def __init__(self, name, type, url):
		super(Workspace, self).__init__(name, type, url)
		
	def is_reachable(self):
		if not os.path.isdir(self.url):
			os.makedirs(self.url)
		if not os.path.isdir(os.path.join(self.url, 'packages')):
			os.makedirs(os.path.join(self.url, 'packages'))
		if not os.path.isdir(os.path.join(self.url, 'artifacts')):
			os.makedirs(os.path.join(self.url, 'artifacts'))
		return True

	def publish(self, item, source):
		if isinstance(source, str):
			src_file = os.path.join(source)
		else:
			src_file = os.path.join(item.location(source), item.basename())
		if not os.path.isfile(src_file):
			raise RepositoryException('Item not found --> ' + item.format_name() + ' : ' + src_file)
		dst_dir = os.path.join(item.location(self.url))
		if not os.path.isdir(dst_dir):
			os.makedirs(dst_dir)
		dst_file = os.path.join(dst_dir, item.basename())
		shutil.copy2(src_file, dst_file)
			