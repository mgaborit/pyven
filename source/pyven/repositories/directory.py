import os, shutil

from pyven.exceptions.exception import PyvenException

from pyven.repositories.repository import Repository
from pyven.exceptions.repository_exception import RepositoryException

class DirectoryRepo(Repository):

	def __init__(self, name, type, url, release=False):
		super(DirectoryRepo, self).__init__(name, type, url, release)

	def is_reachable(self):
		return os.path.isdir(self.url)
		
	def is_available(self, item):
		dir = item.location(self.url)
		dir_ok = os.path.isdir(dir)
		file_ok = False
		if dir_ok:
			file_ok = len(os.listdir(dir)) == 1
		return dir_ok and file_ok
		
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
		if self.release and self.is_available(item):
			raise RepositoryException('Release repository ' + self.name + ' --> ' + item.type() + ' already present : ' + item.format_name())
		src_file = os.path.join(item.location(source.url), item.basename())
		if not os.path.isfile(src_file):
			raise RepositoryException('Item not found --> ' + item.format_name() + ' : ' + src_file)
		dst_dir = os.path.join(item.location(self.url))
		if not os.path.isdir(dst_dir):
			os.makedirs(dst_dir)
		dst_file = os.path.join(dst_dir, item.basename())
		shutil.copy2(src_file, dst_file)
			