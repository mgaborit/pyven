import os, logging, shutil

logger = logging.getLogger('global')

# pym.xml 'repository' node
class Repository(object):

	def __init__(self, id, type, url):
		self.id = id
		self.type = type
		self.url = url

	def retrieve(self, artifact):
		raise NotImplementedError('Invalid call to "retrieve"')
		
	def publish(self, artifact):
		raise NotImplementedError('Invalid call to "publish"')
		
	def factory(node):
		return Repository._factory(node.get('id'), node.get('type'), node.get('url'))
	factory = staticmethod(factory)
	
	def _factory(id, type, url):
		if type == 'file': return FileRepo(id, type, url)
	_factory = staticmethod(_factory)

class FileRepo(Repository):

	def __init__(self, id, type, url):
		super(FileRepo, self, ).__init__(id, type, url)
		
	def retrieve(self, item, workspace):
		src_dir = os.path.join(self.url, item.type()+'s', item.publish_location())
		if os.path.isdir(src_dir):
			src_dir_content = os.listdir(src_dir)
			if len(src_dir_content) == 1:
				item.file = os.path.join(item.workspace_location(workspace), src_dir_content[0])
		dst_dir = item.workspace_location(workspace)
		if not os.path.isdir(dst_dir):
			os.makedirs(dst_dir)
		src_file = os.path.join(src_dir, item.basename())
		dst_file = os.path.join(dst_dir, item.basename())
		shutil.copy(src_file, dst_file)
		
	def publish(self, item, workspace):
		src_file = os.path.join(item.workspace_location(workspace), item.basename())
		if not os.path.isfile(src_file):
			logger.error('Wrong artifact location ' + item.format_name() + ' : ' + src_file)
		dst_dir = os.path.join(self.url, item.type()+'s', item.publish_location())
		if not os.path.isdir(dst_dir):
			os.makedirs(dst_dir)
		dst_file = os.path.join(dst_dir, item.basename())
		shutil.copy(src_file, dst_file)
			
			

			
			
			
			
			