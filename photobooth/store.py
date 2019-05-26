import os
import shutil
from . config import config
from . base import Singleton

class DataStore(Singleton):
    def init_instance(self):
        self.init_paths()
        self.load_backgrounds()

    def init_paths(self):
        self.paths = config["store"]["paths"].copy()
        dir_root = self.paths["root"]
        if not os.path.abspath(dir_root):
            dir_root = os.path.join(os.getcwd(), dir_root)
        self.paths["root"] = dir_root
        for (name, dir_path) in self.paths.items():
            dir_path = os.path.normpath(dir_path)
            if not dir_path.startswith('/'):
                dir_path = os.path.join(dir_root, dir_path)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
            self.paths[name] = dir_path

    def load_backgrounds(self):
        self.backgrounds = {}
        for imgfn in os.listdir(self.paths["backgrounds"]):
            name = os.path.splitext(os.path.split(imgfn)[-1])[0]
            self.backgrounds[name] = os.path.join(self.paths["backgrounds"], imgfn)
    
    def copyinto(self, source, dest, filename=None):
        path = self.paths[dest]
        if filename is None:
            filename = os.path.split(source)[-1]
        target = os.path.join(path, filename)
        shutil.copy(source, target)
        os.chmod(target, 0o664)

    def write(self, fh_read, fn, dest):
        path = self.paths[dest]
        target = os.path.join(path, fn)
        with open(target, 'wb') as fh_write:
            fh_write.write(fh_read.read())

    def get_path(self, catalog, filename=None):
        path = self.paths[catalog]
        if filename:
            path = os.path.join(path, filename)
        return path
