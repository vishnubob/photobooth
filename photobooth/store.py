import os
import shutil
from . config import config
from . base import Singleton

class DataStore(Singleton):
    def init_instance(self):
        self.init_paths()
        self.load_backdrops()

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

    def load_backdrops(self):
        self.backdrops = {}
        for (root, dirs, files) in os.walk(self.paths["backdrops"]):
            for fn in files:
                path = os.path.join(root, fn)
                name = os.path.splitext(os.path.split(path)[-1])[0]
                self.backdrops[name] = path
    
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

    def new_path(self, catalog, *dirpath):
        root = self.paths[catalog]
        new_path = os.path.join(*dirpath)
        new_path = os.path.join(root, new_path)
        os.makedirs(new_path, exist_ok=True)
        return new_path
