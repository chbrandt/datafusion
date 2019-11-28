import os
import sys
import shutil
import collections

from . import utils

class GeoPack(collections.UserDict):
    """
    Data:
     - _tempdir [None] temporary directory if needed for data caching
    """
    _tempdir = None

    def __init__(self, data=None, tempdir=None):
        """
        Dictionary-like structure to handle multi-layered geo data tables

        Input:
         - data: dict
            Layers/tables with geodata; Format: {'label': GeoDataFrame, ...}
         - tempdir: string
            Path/directory to use for occasional data caching
        """
        self._tempdir = tempdir
        super().__init__(data)

    def __del__(self):
        self._remove_tempdir()
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

    @classmethod
    def from_gpkg(cls, filename, tempdir=None):
        # check if filename is url/local
        if utils.is_url(filename):
            # if file is remote/url, we have to cache in a temp dir
            assert cls._tempdir is None
            if tempdir is None:
                # create temp directory
                import tempfile
                tempdir = tempfile.mkdtemp()
            # download (remote) file to (local) temp directory
            try:
                local_filename = utils.download(filename, dst=tempdir)
            except:
                utils.remove_dir(tempdir)
                raise
        else:
            local_filename = filename
        # open it
        data = utils.read_gpkg(local_filename, layers='all')
        # read it into GeoPack
        return cls(data, tempdir=tempdir)

    def _remove_tempdir(self):
        """
        Remove (if created) instance' temp dir. Called during object deletion.
        """
        if self._tempdir:
            # Don't want to 'assert' but that should be true:
            # os.path.exists() and os.path.isdir()
            utils.remove_dir(self._tempdir)
