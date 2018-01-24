import zipfile
import os
import glob
import lxml

from pyven.exceptions.exception import PyvenException
from pyven.items.item import Item

from pyven.logging.logger import Logger

import pyven.utils.utils as utils

class Package(Item):
    EXTENSION = '.zip'

    def __init__(self, company, name, config, version, repo, to_retrieve, publish, items, deliveries, extensions, cwd, patterns, directories):
        super(Package, self).__init__(company, name, config, version, repo, to_retrieve, publish)
        self.items = items
        self.deliveries = deliveries
        self.extensions = extensions
        self.cwd = cwd
        self.patterns = patterns
        self.directories = directories

    def type(self):
        return 'package'
    
    def basename(self):
        return self.format_name('_') + Package.EXTENSION
        
    def pack(self, repo):
        Logger.get().info('Package ' + self.format_name() + ' --> Creating archive ' + self.basename())
        if not os.path.isdir(self.location(repo.url)):
            os.makedirs(self.location(repo.url))
        if os.path.isfile(os.path.join(self.location(repo.url), self.basename())):
            os.remove(os.path.join(self.location(repo.url), self.basename()))
        ok = True
        errors = []
        for item in self.items:
            if not os.path.isfile(os.path.join(item.location(repo.url), item.basename())):
                errors.append('Package item not found --> ' + os.path.join(item.location(repo.url), item.basename()))
                ok = False
        for d in self.directories:
            if not os.path.isdir(os.path.join(self.cwd, d)):
                errors.append('Directory not found --> ' + os.path.join(self.cwd, d))
                ok = False
        if ok:
            zf = zipfile.ZipFile(os.path.join(self.location(repo.url), self.basename()), mode='w')
            try:
                for d in self.directories:
                    Logger.get().info('Package ' + self.format_name() + ' --> Adding directory ' + d)
                    root = os.path.basename(os.path.normpath(os.path.join(self.cwd, d)))
                    for current_dir, dirs, files in os.walk(os.path.join(self.cwd, d)):
                        for f in [os.path.join(current_dir, f) for f in files]:
                            zf.write(os.path.join(self.cwd, f), f[f.find(root):])
                            Logger.get().info('Package ' + self.format_name() + ' --> Added file : ' + f)
                    Logger.get().info('Package ' + self.format_name() + ' --> Added directory ' + d)
                for pattern in self.patterns:
                    for file in glob.glob(os.path.join(self.cwd, pattern)):
                        zf.write(file, os.path.basename(file))
                        Logger.get().info('Package ' + self.format_name() + ' --> Added file from pattern : ' + os.path.basename(file))
            finally:
                zf.close()
                Logger.get().info('Package ' + self.format_name() + ' --> Created archive ' + self.basename())
                utils.str_to_file(self.to_xml(), os.path.join(self.location(repo.url), self.format_name('_') + '.xml'))
        else:
            e = PyvenException('')
            e.args = tuple(errors)
            raise e
        return ok
            
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
    
    def deliver(self, dir, repo):
        if len(self.deliveries) < 1:
            self.unpack(dir, repo, flatten=False)
        else:
            for delivery in self.deliveries: 
                self.unpack(os.path.join(dir, delivery), repo, flatten=True)
          
    def to_xml(self, pretty_print=True):
        root_node = lxml.etree.Element("package")
        for i in self.items:
            i_node = lxml.etree.SubElement(root_node, "item")
            i_node.text = i.format_name()
        for pattern in self.patterns:
            for file in glob.glob(os.path.join(self.cwd, pattern)):
                p_node = lxml.etree.SubElement(root_node, "pattern")
                p_node.text = os.path.basename(file)
        for d in self.directories:
            root = os.path.basename(os.path.normpath(os.path.join(self.cwd, d)))
            for current_dir, dirs, files in os.walk(os.path.join(self.cwd, d)):
                for f in [os.path.join(current_dir, f) for f in files]:
                    d_node = lxml.etree.SubElement(root_node, "directory")
                    d_node.text = f[f.find(root):]
        return lxml.etree.tostring(root_node, pretty_print=pretty_print).decode("utf-8")
        
