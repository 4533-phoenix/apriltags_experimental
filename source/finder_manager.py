from multiprocessing.pool import Pool
from finder import Finder

class FinderManager:
    def __init__(self, cameras, networktable_ip):
        self.cameras = cameras
        self.networktable_ip = networktable_ip
        self.pool = Pool(len(self.cameras))

    def start(self):
        self.pool.starmap_async(Finder, self.cameras)

    def stop(self):
        self.pool.close()
        self.pool.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()