from pyven.reporting.html_utils import HTMLUtils

class ListingGenerator(object):

	def __init__(self, title, properties={}, generators=[]):
		self.title = title
		self.properties = properties
		self.generators = generators
		
	@HTMLUtils.listing
	def generate(self):
		str = self._generate_title(self.title)
		if len(self.properties) > 0:
			str += self._generate_properties()
		if len(self.generators) > 0:
			str += self._generate_listing()
		return str
		
	@HTMLUtils.listing_properties
	def _generate_properties(self):
		str = ''
		for name, value in self.properties.items():
			str += self._generate_property(name, value)
		return str

	@HTMLUtils.listing_title
	def _generate_title(self, title):
		return title
	
	@HTMLUtils.listing_property
	def _generate_property(self, name, value):
		return name + ' : ' + value
	
	def _generate_listing(self):
		str = ''
		for generator in self.generators:
			str += generator.generate()
		return str
		