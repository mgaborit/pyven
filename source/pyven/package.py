import logging, zipfile, os

logger = logging.getLogger('global')

from item import Item

# pym.xml 'package' node
class Package(Item):
	EXTENSION = '.zip'

	def __init__(self, node):
		super(Package, self).__init__(node)
		self.items = []
		
	def workspace_location(self, workspace):
		return os.path.join(workspace, 'packages')

	def type(self):
		return 'package'
	
	def basename(self):
		return self.format_name('_') + Package.EXTENSION
		
	def pack(self, workspace):
		zip_name = os.path.join(self.workspace_location(workspace), self.basename())
		logger.info('Creating archive : ' + zip_name)
		zf = zipfile.ZipFile(zip_name, mode='w')
		try:
			for item in self.items:
				if not os.path.isfile(item.file):
					raise Exception('Package item not found : ' + item.file)
				else:
					item_file = os.path.join(item.workspace_location(workspace), os.path.basename(item.file))
					zf.write(item_file, os.path.basename(item_file))
					logger.info('Added artifact ' + item.format_name() + ' to archive ' + zip_name)
		finally:
			logger.info('Created archive : ' + zip_name)
			zf.close()
			
	def unpack(self, dir):
		with zipfile.ZipFile(os.path.join(self.workspace_location(), self.basename()), "r") as z:
			z.extractall(dir)