from pyven.reporting.html_utils import HTMLUtils

from pyven.reporting.generator import Generator

class ListingGenerator(Generator):

	def __init__(self, title, properties={}, generators=[]):
		super(ListingGenerator, self).__init__()
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
			if name.upper() == 'STATUS':
				str += self._generate_property(name, self._generate_status(value))
			else:
				str += self._generate_property(name, value)
		return str

	@HTMLUtils.listing_title
	def _generate_title(self, title):
		return title
	
	@HTMLUtils.listing_property
	def _generate_property(self, name, value):
		return name + ' : ' + value
	
	@HTMLUtils.listing_property_status
	def _generate_status(self, value):
		return value
	
	def _generate_listing(self):
		str = ''
		for generator in self.generators:
			str += generator.generate()
		return str
		