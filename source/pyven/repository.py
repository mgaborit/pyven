import os, logging, shutil

logger = logging.getLogger('global')

# pym.xml 'repository' node
class Repository(object):
	AVAILABLE_TYPES = ['file']
	
	def __init__(self, name, type, url):
		self.name = name
		self.type = type
		if self.type not in Repository.AVAILABLE_TYPES:
			raise Exception('Wrong repository type : ' + self.type, 'Available types : ' + str(Repository.AVAILABLE_TYPES))
		self.url = url

	def retrieve(self, artifact):
		raise NotImplementedError
		
	def publish(self, artifact):
		raise NotImplementedError
		
	def factory(node):
		return Repository._factory(node.get('name'), node.get('type'), node.get('url'))
	factory = staticmethod(factory)
	
	def _factory(name, type, url):
		if type not in Repository.AVAILABLE_TYPES:
			raise Exception('Wrong repository type : ' + type, 'Available types : ' + str(Repository.AVAILABLE_TYPES))
		if type == 'file': return FileRepo(name, type, url)
	_factory = staticmethod(_factory)

class FileRepo(Repository):

	def __init__(self, name, type, url):
		super(FileRepo, self, ).__init__(name, type, url)
		
	def retrieve(self, item, workspace):
		src_dir = item.location(self.url)
		if os.path.isdir(src_dir):
			src_dir_content = os.listdir(src_dir)
			if len(src_dir_content) == 1:
				item.file = os.path.join(item.location(workspace), src_dir_content[0])
		dst_dir = item.location(workspace)
		if not os.path.isdir(dst_dir):
			os.makedirs(dst_dir)
		src_file = os.path.join(src_dir, item.basename())
		dst_file = os.path.join(dst_dir, item.basename())
		shutil.copy(src_file, dst_file)
		
	def publish(self, item, workspace):
		src_file = os.path.join(item.location(workspace), item.basename())
		if not os.path.isfile(src_file):
			raise Exception('Wrong artifact location ' + item.format_name() + ' : ' + src_file)
		dst_dir = os.path.join(item.location(self.url))
		if not os.path.isdir(dst_dir):
			os.makedirs(dst_dir)
		dst_file = os.path.join(dst_dir, item.basename())
		shutil.copy(src_file, dst_file)
			