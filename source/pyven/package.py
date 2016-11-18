import logging, zipfile, os, shutil

logger = logging.getLogger('global')

from item import Item

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
		logger.info('Creating archive : ' + self.basename())
		if not os.path.isdir(self.location(repo)):
			os.makedirs(self.location(repo))
		zf = zipfile.ZipFile(os.path.join(self.location(repo), self.basename()), mode='w')
		try:
			for item in self.items:
				if not os.path.isfile(item.file):
					raise Exception('Package item not found : ' + item.file)
				else:
					zf.write(os.path.join(item.location(repo), item.basename()), os.path.join(self.format_name('_'), item.basename()))
					logger.info('Added artifact ' + item.format_name() + ' to archive ' + self.basename())
		finally:
			logger.info('Created archive : ' + self.basename())
			zf.close()
			
	def unpack(self, dir, repo, flatten=False):
		if not os.path.isfile(os.path.join(self.location(repo), self.basename())):
			raise Exception('Package not found at ' + self.location(repo) + ' : ' + self.format_name())
		if not os.path.isdir(dir):
			os.makedirs(dir)
		if flatten:
			with zipfile.ZipFile(os.path.join(self.location(repo), self.basename())) as z:
				for member in z.namelist():
					filename = os.path.basename(member)
					# skip directories
					if filename:
						# copy file (taken from zipfile's extract)
						source = z.open(member)
						target = file(os.path.join(dir, filename), "wb")
						with source, target:
							shutil.copyfileobj(source, target)
		else:
			with zipfile.ZipFile(os.path.join(self.location(repo), self.basename()), "r") as z:
				z.extractall(dir)