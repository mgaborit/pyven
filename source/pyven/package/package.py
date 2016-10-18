import logging, zipfile, os

logger = logging.getLogger('global')

# pym.xml 'package' node
class Package(object):

	def __init__(self, node):
		self.group = node.get('group')
		self.id = node.get('id')
		self.version = node.get('version')
		self.items = []
		
	def format_name(self, separator=':'):
		return self.group + separator + self.id + separator + self.version
	
	def zip(self, workspace):
		zip_name = os.path.join(workspace, 'packages', self.format_name('_') + '.zip')
		logger.info('Creating archive : ' + zip_name)
		zf = zipfile.ZipFile(zip_name, mode='w')
		try:
			for item in self.items:
				item_name = os.path.join(workspace, 'artifacts', item.group, item.id, item.version, os.path.basename(item.file))
				zf.write(item_name, os.path.basename(item_name))
				logger.info('Added artifact ' + item.format_name() + ' to archive ' + zip_name)
		finally:
			logger.info('Created archive : ' + zip_name)
			zf.close()