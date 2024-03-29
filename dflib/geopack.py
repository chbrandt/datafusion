import os
import sys
import shutil
import collections

from . import utils
from .log import *


class GeoPack(collections.UserDict):
    """
    Data:
     - _tempdir [None] temporary directory if needed for data caching
    """
    _tempdir = None

    def __init__(self, data=None, file=None, tempdir=None):
        """
        Dictionary-like structure to handle multi-layered geo data tables

        Input:
         - data: dict
            Layers/tables with geodata; Format: {'label': GeoDataFrame, ...}
         - tempdir: string
            Path/directory to use for occasional data caching
        """
        if tempdir is not None:
            assert os.path.isdir(tempdir), print("Expected to find 'tempdir'")
            self._tempdir = {'path':tempdir, 'generated':False}
        else:
            self._tempdir = {'path':utils.create_tempdir(), 'generated':True}
        if file is not None:
            data = self._read_gpkg(file)
        super().__init__(data)

    def __del__(self):
        try:
            self._remove_tempdir()
        except Exception as err:
            logerr("{!s}".format(err))
        try:
            super().__del__()
        except:
            pass

    @property
    def list(self):
        return list(self.data.keys())

    @property
    def info(self):
        for k,v in self.data.items():
            print("{!s}:".format(k))
            print("\tCRS:{!s}".format(v.crs))
            print()

    def _read_gpkg(self, filename):
        assert all(a in self._tempdir for a in ['path','generated'])
        tempdir = self._tempdir
        # check if filename is url/local
        if utils.is_url(filename):
            # if file is remote/url, we have to cache in a temp dir
            # download (remote) file to (local) temp directory
            try:
                local_filename = utils.download(filename, dst=tempdir['path'])
            except:
                self._remove_tempdir()
                raise
        else:
            local_filename = filename
        # open it
        data = utils.read_gpkg(local_filename, layers='all')
        return data

    def _remove_tempdir(self):
        """
        Remove (if created) instance' temp dir. Called during object deletion.
        """
        if self._tempdir:
            assert all(a in self._tempdir for a in ['path','generated'])
            # Don't want to 'assert' but that should be true:
            # os.path.exists() and os.path.isdir()
            if self._tempdir['generated']:
                utils.remove_dir(self._tempdir['path'])


def _define_tempdir(path, generated=False):
    return dict(path=path, generated=generated)
