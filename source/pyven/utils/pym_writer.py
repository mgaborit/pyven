from lxml import etree
import os

import pyven.constants
from pyven.utils.utils import str_to_file

class PymWriter(object):
    TAB = '  '
    TAGS_STACK = []
    PYM = 'pym.xml'
        
    @staticmethod
    def indent():
        indent = ""
        for tag in PymWriter.TAGS_STACK:
            indent += PymWriter.TAB
        return indent
        
    @staticmethod
    def ltag(name, attributes={}):
        tag = '<' + name
        if len(attributes) > 0:
            tag += ' '
        return tag + ' '.join([k + '="' + v + '"' for k, v in attributes.items()]) + '>'
    
    @staticmethod
    def rtag(name):
        return '</' + name + '>'
    
    @staticmethod
    def tags(content, name, attributes={}, oneline=False):
        result = PymWriter.indent() + PymWriter.ltag(name, attributes)
        if not oneline:
            PymWriter.TAGS_STACK.append(name)
            result += '\n'
            result += PymWriter.indent()
        try:
            result += content
            if not oneline:
                result += '\n'
                result += PymWriter.indent()
                PymWriter.TAGS_STACK.pop()
        finally:
            result += PymWriter.rtag(name) + '\n'
        return result

    @staticmethod
    def comment(text):
        return PymWriter.indent() + '<!-- ' + text + ' -->'

    @staticmethod
    def write():
        if not os.path.isfile(PymWriter.PYM):
            pyven_tag = PymWriter.tags(PymWriter.tags(PymWriter.comment('Write your project title here'), 'project', oneline=True)\
                                        + PymWriter.tags(PymWriter.comment('Declare your constants here'), 'constants')\
                                        + PymWriter.tags(PymWriter.tags(PymWriter.comment('Declare your repositories here'), 'repositories')\
                                                        + PymWriter.tags(PymWriter.comment('Declare your artifacts here'), 'artifacts')\
                                                        + PymWriter.tags(PymWriter.comment('Declare your packages here'), 'packages')\
                                                        + PymWriter.tags(PymWriter.tags(PymWriter.comment('Declare your tools here'), 'tools'), 'build')\
                                                        + PymWriter.tags(PymWriter.comment('Declare your tests here'), 'tests')\
                                        , 'platform', {'name' : pyven.constants.PLATFORM})\
                        , 'pyven', {'version' : pyven.constants.VERSION})
            str_to_file(pyven_tag, PymWriter.PYM)
        
    