import h5py
import numpy as np

f = h5py.File("file5.hdf5", 'w')

dset = f.create_dataset("my_dataset", (10, 10), dtype='f')

dset[0,0] = 2.0
f.close