import os, logging, shutil

from pyven.exceptions.exception import PyvenException

from pyven.repositories.repository import Repository
from pyven.exceptions.repository_exception import RepositoryException

logger = logging.getLogger('global')

class DirectoryRepo(Repository):

	def __init__(self, name, type, url):
		super(DirectoryRepo, self, ).__init__(name, type, url)
		
	@classmethod
	def from_node(cls, node):
		return cls(node.get('name'), node.get('type'), node.get('url'))

	def is_available(self):
		return os.path.isdir(self.url)
		
	def retrieve(self, item, destination):
		src_dir = item.location(self.url)
		if os.path.isdir(src_dir):
			src_dir_content = os.listdir(src_dir)
			if len(src_dir_content) == 1:
				item.file = os.path.join(item.location(destination.url), src_dir_content[0])
		dst_dir = item.location(destination.url)
		if not os.path.isdir(dst_dir):
			os.makedirs(dst_dir)
		src_file = os.path.join(src_dir, item.basename())
		dst_file = os.path.join(dst_dir, item.basename())
		shutil.copy2(src_file, dst_file)
		
	def publish(self, item, source):
		src_file = os.path.join(item.location(source.url), item.basename())
		if not os.path.isfile(src_file):
			raise RepositoryException('Item not found --> ' + item.format_name() + ' : ' + src_file)
		dst_dir = os.path.join(item.location(self.url))
		if not os.path.isdir(dst_dir):
			os.makedirs(dst_dir)
		dst_file = os.path.join(dst_dir, item.basename())
		shutil.copy2(src_file, dst_file)
			