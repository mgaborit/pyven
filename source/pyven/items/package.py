import logging, zipfile, os, shutil

from pyven.exceptions.exception import PyvenException

logger = logging.getLogger('global')

from pyven.items.item import Item

# pym.xml 'package' node
class Package(Item):
	EXTENSION = '.zip'

	def __init__(self, node):
		super(Package, self).__init__(node)
		self.items = []
		
	def type(self):
		return 'package'
	
	def basename(self):
		return self.format_name('_') + Package.EXTENSION
		
	def pack(self, repo):
		logger.info('Package ' + self.format_name() + ' --> Creating archive ' + self.basename())
		if not os.path.isdir(self.location(repo.url)):
			os.makedirs(self.location(repo.url))
		if os.path.isfile(os.path.join(self.location(repo.url), self.basename())):
			os.remove(os.path.join(self.location(repo.url), self.basename()))
		zf = zipfile.ZipFile(os.path.join(self.location(repo.url), self.basename()), mode='w')
		try:
			for item in self.items:
				if not os.path.isfile(item.file):
					logger.error('Package item not found --> ' + item.file)
					return False
				else:
					zf.write(os.path.join(item.location(repo.url), item.basename()), item.basename())
					logger.info('Package ' + self.format_name() + ' --> Added artifact ' + item.format_name())
		finally:
			logger.info('Package ' + self.format_name() + ' --> Created archive ' + self.basename())
			zf.close()
		return True
			
	def unpack(self, dir, repo, flatten=False):
		if not os.path.isfile(os.path.join(self.location(repo.url), self.basename())):
			raise PyvenException('Package not found at ' + self.location(repo.url) + ' : ' + self.format_name())
		if not os.path.isdir(dir):
			os.makedirs(dir)
		if flatten:
			with zipfile.ZipFile(os.path.join(self.location(repo.url), self.basename()), "r") as z:
				z.extractall(dir)
		else:
			with zipfile.ZipFile(os.path.join(self.location(repo.url), self.basename()), "r") as z:
				z.extractall(os.path.join(dir, self.format_name('_')))