import hashlib
import codecs
import os

from lxml import etree

from pyven.exceptions.parser_exception import ParserException

def hash(str, hash='ripemd160', encoding='utf-8'):
	h = hashlib.new(hash)
	h.update(str.encode(encoding))
	return h.hexdigest()
	
def str_to_file(str, filename):
	file = codecs.open(filename, 'w', 'utf-8')
	file.write(str)
	file.close()
	
def file_to_str(filename):
	file = codecs.open(filename, 'r', 'utf-8')
	str = file.read()
	file.close()
	return str
		
def parse_xml(file):
    tree = None
    if not os.path.isfile(file):
        raise ParserException('File not found : ' + file)
    try:
        tree = etree.parse(file)
    except Exception as e:
        pyven_exception = ParserException('')
        pyven_exception.args = e.args
        raise pyven_exception
    return tree
    