import zipfile, os

from pyven.exceptions.exception import PyvenException
from pyven.items.item import Item

from pyven.logging.logger import Logger

class Package(Item):
    EXTENSION = '.zip'

    def __init__(self, company, name, config, version, repo, to_retrieve, publish, items, delivery, extensions):
        super(Package, self).__init__(company, name, config, version, repo, to_retrieve, publish)
        self.items = items
        self.delivery = delivery
        self.extensions = extensions

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
        if ok:
            zf = zipfile.ZipFile(os.path.join(self.location(repo.url), self.basename()), mode='w')
            try:
                for item in self.items:
                    zf.write(os.path.join(item.location(repo.url), item.basename()), item.basename())
                    Logger.get().info('Package ' + self.format_name() + ' --> Added artifact ' + item.format_name())
            finally:
                zf.close()
                Logger.get().info('Package ' + self.format_name() + ' --> Created archive ' + self.basename())
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
        if self.delivery == '':
            self.unpack(dir, repo, flatten=False)
        else:
            self.unpack(os.path.join(dir, self.delivery), repo, flatten=True)