# -*- coding: utf-8 -*-
"""Read image data from various format files.

This module provides low level file format support to `xtomo_importer`_ 

Supported image fomats include TIFF, PackBits and LZW encoded TIFF, 
HDF5 (Data Exchange and NeXuS), HDF4 (NeXuS), SPE, TXRM, XRM, EDF, 
DPT, netCDF. 

:Author:
  `Francesco De Carlo <mailto: decarlof@gmail.com>`_

:Organization:
  Argonne National Laboratory, Argonne, IL 60439 USA

:Version: 2014.08.15

Requirements
------------
* `h5py <http://www.h5py.org/>`_ 
* `netCDF <https://pypi.python.org/pypi/netCDF4>`_  (optional for supporting APS 13-BM data)
* `pyhdf <https://pypi.python.org/pypi/pyhdf>`_  (optional for supporting APS 2-BM data)
* `PIL.Image <http://www.pythonware.com/products/pil/>`_ 
* `Tifffile.c 2013.01.18 <http://www.lfd.uci.edu/~gohlke/>`_ (optional for supporting Elettra data) (recommended for faster decoding of PackBits and LZW encoded strings)

Notes
-----
PackBits and LZW encoded TIFF tested on little-endian platforms only.

Examples
--------

>>> f = XTomoReader(_file_name)
>>> if (data_type is 'hdf4'):
>>>     tmpdata = f.hdf4(x_start=slices_start,
>>>                         x_end=slices_end,
>>>                         x_step=slices_step,
>>>                         array_name='data')


.. _xtomo_importer: dataexchange.xtomo.xtomo_importer.html
"""

import h5py
from pyhdf import SD
import numpy as np 
import PIL.Image as Image
import netCDF4 as nc
import math
import os
from scipy import misc

import formats.xradia_xrm as xradia
import formats.data_struct as dstruct
import formats.data_spe as spe

from formats.EdfFile import EdfFile
from formats.tifffile import TiffFile

class XTomoReader:

    def __init__(self, file_name):
        self.file_name = file_name

    def hdf5(self,
             array_name=None,
             x_start=0,
             x_end=0,
             x_step=1,
             y_start=0,
             y_end=0,
             y_step=1,
             z_start=0,
             z_end=0,
             z_step=1):
        """ 
        Read 3-D tomographic projection data from a Data Exchange HDF5 file.

        Opens ``file_name`` and reads the contents of the 3D array specified 
	    by ``array_name`` in the specified group of the HDF5 file.
        
        Parameters
        ----------
        file_name : str
            Input HDF5 file.
        
        array_name : str
            Name of the array to be read at in the exchange group.
        
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        z_start, z_end, z_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        Returns
        -------
        out : ndarray
            Returns the data as a matrix.
        """
        # Read data from file.
        f = h5py.File(self.file_name, 'r')
	try:
		hdfdata = f[array_name]
		if (array_name.split('/')[1] == "theta"):
			num_z = hdfdata.size
        		if z_end is 0:
            			z_end = num_z        		
			# Construct theta.
        		dataset = hdfdata[z_start:z_end:z_step]
		else:	
			num_z, num_y, num_x = hdfdata.shape
        		if x_end is 0:
            			x_end = num_x
        		if y_end is 0:
        			y_end = num_y
        		if z_end is 0:
            			z_end = num_z
        		# Construct dataset.
        		dataset = hdfdata[z_start:z_end:z_step,
                          			y_start:y_end:y_step,
                          			x_start:x_end:x_step]
	except KeyError:
                print "FILE DOES NOT CONTAIN A VALID TOMOGRAPHY DATA SET"
		dataset = None        

	f.close()

        return dataset
                
    def nxs(self,
             array_type=None,
             x_start=0,
             x_end=0,
             x_step=1,
             y_start=0,
             y_end=0,
             y_step=1,
             z_start=0,
             z_end=0,
             z_step=1):
        """ 
        Read 3-D tomographic projection data from a NeXuS HDF5 file.

        Opens ``file_name`` and reads the contents of the 3D array specified 
	    by ``array_name`` in the specified group of the HDF5 file.
        
        Parameters
        ----------
        file_name : str
            Input HDF5 file.
        
        array_name : str
            Name of the array to be read at in the NeXuS file.
            Options are: projections, dark, white 
        
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        z_start, z_end, z_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        Returns
        -------
        out : ndarray
            Returns the data as a matrix.
        """
        # Read data from file.
        array_name = 'entry1/tomo_entry/instrument/detector/data'
        image_key_name = 'entry1/tomo_entry/instrument/detector/image_key'
        print array_name
        print array_type

        if (array_type == 'projections'):
            image_key_value = 0
        if (array_type == 'white'):
            image_key_value = 1                    
        if (array_type == 'dark'):
            image_key_value = 2

        print image_key_value
        
        f = h5py.File(self.file_name, 'r')
  	try:
		hdfdata = f[array_name]
		if (array_name.split('/')[1] == "theta"):
			num_z = hdfdata.size
        		if z_end is 0:
            			z_end = num_z        		
			# Construct theta.
        		dataset = hdfdata[z_start:z_end:z_step]
		else:	
                        image_key = f[image_key_name].value
                        image_location = np.where(image_key == image_key_value)
                        dataset = np.ndarray.take(hdfdata.value, image_location[0], axis = 0)
			num_z, num_y, num_x = dataset.shape
        		if x_end is 0:
            			x_end = num_x
        		if y_end is 0:
        			y_end = num_y
        		if z_end is 0:
            			z_end = num_z
        		# Construct dataset.
                        print "Z:", z_start, z_end, z_step
                        print "Y:", y_start, y_end, y_step
                        print "X:", x_start, x_end, x_step
        		dataset = dataset[z_start:z_end:z_step,
                          			y_start:y_end:y_step,
                          			x_start:x_end:x_step]
                        print dataset.shape
	except KeyError:
                print "FILE DOES NOT CONTAIN A VALID TOMOGRAPHY DATA SET"
		dataset = None        

	f.close()
        return dataset

    def hdf4(self,
             array_name=None,
             x_start=0,
             x_end=0,
             x_step=1,
             y_start=0,
             y_end=0,
             y_step=1):
        """ 
        Read 2-D tomographic projection data from an HDF4 file.

        Opens ``file_name`` and reads the contents
        of the array specified by ``array_name`` in
        the specified group of the HDF file.
        
        Parameters
        ----------
        file_name : str
            Input HDF file.
        
        array_name : str
            Name of the array to be read at exchange group.
        
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        Returns
        -------
        out : ndarray
            Returns the data as a matrix.
        """
        # Read data from file.
        f = SD.SD(self.file_name)
        sds = f.select(array_name)
        hdfdata = sds.get()
        sds.endaccess()
        f.end()
	
        num_y, num_x = hdfdata.shape
	if x_end is 0:
            x_end = num_x
        if y_end is 0:
            y_end = num_y

        # Construct dataset.
        dataset = hdfdata[x_start:x_end:x_step,
                          y_start:y_end:y_step]
        return dataset
        
    def hdf5_2d(self,
             array_name=None,
             x_start=0,
             x_end=None,
             x_step=1,
             y_start=0,
             y_end=None,
             y_step=1):
        """ 
        Read 2-D tomographic projection data from an HDF5 file.

        Opens ``file_name`` and reads the contents
        of the array specified by ``array_name`` in
        the specified group of the HDF file.
        
        Parameters
        ----------
        file_name : str
            Input HDF file.
        
        array_name : str
            Name of the array to be read at exchange group.
        
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        Returns
        -------
        out : ndarray
            Returns the data as a matrix.
        """
        # Read data from file.
        f = h5py.File(self.file_name, 'r')
        hdfdata = f[array_name]

        num_x, num_y = hdfdata.shape
        if x_end is None:
            x_end = num_x
        if y_end is None:
            y_end = num_y

        # Construct dataset.
        dataset = hdfdata[x_start:x_end:x_step,
                          y_start:y_end:y_step]
        f.close()
        return dataset
        
    def tiff(self, 
             x_start=0,
             x_end=0,
             x_step=1,
             y_start=0,
             y_end=0,
             y_step=1,
             dtype='uint16'
             ):
             
        """
        Read 2-D tomographic projection data from a TIFF file.

        Parameters
        ----------
        file_name : str
            Name of the input TIFF file.
        
        dtype : str, optional
            Corresponding numpy data type of the TIFF file.
        
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        Returns
        -------
        out : ndarray
            Output 2-D matrix as numpy array.
        """
#        This ONLY works on little-endian platforms only
#        im = Image.open(self.file_name)
#        out = np.fromstring(im.tostring(), dtype).reshape(
#                               tuple(list(im.size[::-1])))


#        This seeem to work on both big and little-endian platforms
        out = misc.imread(self.file_name)
        num_x, num_y = out.shape

        if x_end is 0:
            x_end = num_x
        if y_end is 0:
            y_end = num_y
        
        #im.close()
        return out[x_start:x_end:x_step,
                   y_start:y_end:y_step]
        
    def tiffc(self, 
              dtype='uint16',
              x_start=0,
              x_end=0,
              x_step=1,
              y_start=0,
              y_end=0,
              y_step=1):
        """
        Read 2-D complex(!) tomographic projection data from a TIFF file.

        Parameters
        ----------
        file_name : str
            Name of the input TIFF file.
        
        dtype : str, optional
            Corresponding Numpy data type of the TIFF file.
        
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole ndarray.
        
        Returns
        -------
        out : ndarray
            Output 2-D matrix as numpy array.
        """
        im = TiffFile(self.file_name)
        out = im[0].asarray()

        num_x, num_y = out.shape
        if x_end is 0:
            x_end = num_x
        if y_end is 0:
            y_end = num_y
        
        #im.close()
        return out[x_start:x_end:x_step,
                   y_start:y_end:y_step]
        
    def txrm(self,
             array_name=None,
             x_start=0,
             x_end=0,
             x_step=1,
             y_start=0,
             y_end=0,
             y_step=1,
             z_start=0,
             z_end=0,
             z_step=1):
        """ 
        Read 3-D tomographic projection data from a TXRM file 
        
        Parameters
        ----------
        file_name : str
            Input txrm file.
        
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        z_start, z_end, z_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        Returns
        -------
        out : array
            Returns the data as a matrix.
        """
        # Read data from file.
        reader = xradia.xrm()
        array = dstruct

        try:
            reader.read_txrm(self.file_name,array)
            if (array_name == "theta"):
                theta = np.asarray(array.exchange.angles)                
                num_z = theta.size
        	if z_end is 0:
                    z_end = num_z
		# Construct theta.
        	dataset = theta[z_start:z_end:z_step]
            else:
                data = np.asarray(array.exchange.data)
                num_x, num_y, num_z = np.shape(array.exchange.data)
                data = np.swapaxes(data,0,2)
                num_z, num_y, num_x = np.shape(data)
                if x_end is 0:
                    x_end = num_x
                if y_end is 0:
                    y_end = num_y
                if z_end is 0:
                    z_end = num_z
                # Construct dataset from desired z, y, x.
                dataset = data[z_start:z_end:z_step,
                                y_start:y_end:y_step,
                                x_start:x_end:x_step]                
        except KeyError:
            dataset = None

        return dataset
       
    def xrm(self,
            x_start=0,
            x_end=0,
            x_step=1,
            y_start=0,
            y_end=0,
            y_step=1,
            z_start=0,
            z_end=0,
            z_step=1):
        """ 
        Read 3-D tomographic projection data from an XRM file.
        
        Parameters
        ----------
        file_name : str
            Input xrm file.
        
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        z_start, z_end, z_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        Returns
        -------
        out : array
            Returns the data as a matrix.
        """
        # Read data from file.
        reader = xradia.xrm()
        array = dstruct

        try:
            reader.read_xrm(self.file_name,array)
            data = np.asarray(array.exchange.data)
            num_x, num_y, num_z = np.shape(array.exchange.data)
            data = np.swapaxes(data,0,2)
            num_z, num_y, num_x = np.shape(data)
            if x_end is 0:
                x_end = num_x
            if y_end is 0:
                y_end = num_y
            if z_end is 0:
                z_end = num_z
            # Construct dataset from desired z, y, x.
            dataset = data[z_start:z_end:z_step,
                            y_start:y_end:y_step,
                            x_start:x_end:x_step]                
        except KeyError:
            dataset = None

        return dataset
        
    def spe(self,
            x_start=0,
            x_end=0,
            x_step=1,
            y_start=0,
            y_end=0,
            y_step=1,
            z_start=0,
            z_end=0,
            z_step=1):
        """ 
        Read 3-D tomographic projection data from a SPE file.
        
        Parameters
        ----------
        file_name : str
            Input spe file.

        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        z_start, z_end, z_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        Returns
        -------
        out : array
            Returns the data as a matrix.
        """
        spe_data = spe.PrincetonSPEFile(self.file_name)
        array = spe_data.getData()
        num_z, num_y, num_x = np.shape(array)

        if x_end is 0:
            x_end = num_x
        if y_end is 0:
            y_end = num_y
        if z_end is 0:
            z_end = num_z

        # Construct dataset from desired y.
        dataset = array[z_start:z_end:z_step,
                        y_start:y_end:y_step,
                        x_start:x_end:x_step]
        return dataset
        
    def edf(self,
             x_start=0,
             x_end=0,
             x_step=1,
             y_start=0,
             y_end=0,
             y_step=1,
             z_start=0,
             z_end=0,
             z_step=1):
        """ 
        Read 3-D tomographic projection data from an EDF (ESRF) file.
        
        Parameters
        ----------
        file_name : str
            Input edf file.
            
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        z_start, z_end, z_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        Returns
        -------
        out : array
            Returns the data as a matrix.
        """
 
        # Read data from file.
        f = EdfFile(self.file_name, access='r')
        dic = f.GetStaticHeader(0)
        tmpdata = np.empty((f.NumImages, int(dic['Dim_2']), int(dic['Dim_1'])))

        for (i, ar) in enumerate(tmpdata):
            tmpdata[i::] = f.GetData(i)

        num_z, num_y, num_x = np.shape(tmpdata)
        if x_end is 0:
            x_end = num_x
        if y_end is 0:
            y_end = num_y
        if z_end is 0:
            z_end = num_z

        # Construct dataset from desired y.
        dataset = tmpdata[z_start:z_end:z_step,
                          y_start:y_end:y_step,
                          x_start:x_end:x_step]
        return dataset
        
    def dpt(self,
             x_start=0,
             x_end=0,
             x_step=1,
             y_start=0,
             y_end=0,
             y_step=1,
             z_start=0,
             z_end=0,
             z_step=1):
        """ 
        Read 3-D tomographic projection data from a DPT (SRC) file.
        
        Parameters
        ----------
        file_name : str
            Input dpt file.
            
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        z_start, z_end, z_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        Returns
        -------
        out : array
            Returns the data as a matrix.
        """
 
        # Read data from file.
        offset = 2

        # Count the number of projections
        file = open(self.file_name, 'r')
        num_of_projections = sum(1 for line in file)
        file.close()

        # Determine image size and dimentions        
        file = open(self.file_name, 'r')
        first_line = file.readline()
        firstlinelist=first_line.split(",")

        image_size = len(firstlinelist)-offset
        image_dim = int(math.sqrt(image_size))
        file.close()

        tmpdata = np.empty((num_of_projections, image_dim, image_dim))
 
        num_z, num_y, num_x = np.shape(tmpdata)

        if image_dim**2 == image_size: # check projections are square
            print "Reading ", os.path.basename(self.file_name)
            file = open(self.file_name, 'r')      
            for line in file:
                linelist=line.split(",")

                projection = np.reshape(np.array(linelist)[offset:], (image_dim ,image_dim))

                projection = projection.transpose()
                projection = projection.astype(np.float)
                projection = np.exp(-projection)

                tmpdata[int(linelist[0])::] = projection

            file.close()

        if x_end is 0:
            x_end = num_x
        if y_end is 0:
            y_end = num_y
        if z_end is 0:
            z_end = num_z

        # Construct dataset from desired y.
        dataset = tmpdata[z_start:z_end:z_step,
                          y_start:y_end:y_step,
                          x_start:x_end:x_step]

        return dataset
       
    def netcdf(self,
               x_start=0,
               x_end=0,
               x_step=1,
               y_start=0,
               y_end=0,
               y_step=1,
               z_start=0,
               z_end=0,
               z_step=1):
        """ 
        Read 3-D tomographic projection data from a netCDF file.

       
        Parameters
        ----------
        file_name : str
            Input netcdf file.
        
        x_start, x_end, x_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        y_start, y_end, y_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        z_start, z_end, z_step : scalar, optional
            Values of the start, end and step of the
            slicing for the whole array.
        
        Returns
        -------
        out : array
            Returns the data as a matrix.
        """
        nc_data = nc.Dataset(self.file_name, 'r')
        array = nc_data.variables['array_data'][:]
            
        num_z, num_y, num_x = np.shape(array)
        if x_end is 0:
            x_end = num_x
        if y_end is 0:
            y_end = num_y
        if z_end is 0:
            z_end = num_z

        # Construct dataset from desired y.
        dataset = array[z_start:z_end:z_step,
                        y_start:y_end:y_step,
                        x_start:x_end:x_step]
        return dataset
    
    def hdf5_test(self,
                     array_name=None,
                     x_start=0,
                     x_end=None,
                     x_step=1,
                     y_start=0,
                     y_end=None,
                     y_step=1,
                     z_start=0,
                     z_end=None,
                     z_step=1):

        # expand the file_name
        file_name = os.path.abspath(self.file_name)

        # open the hdf file with context manager so it will always close
        # properly, even if there are uncaught errors.
        with h5py.File(file_name, "r") as f:
            # set up all of the slices, these should really be passed in
            # and follow the pattern
            # if a is None:
            #    a = slice(None, None, None)
            hdfdata = f[array_name]
            num_z, num_y, num_x = hdfdata.shape

            if x_end is None:
            	x_end = num_x
            if y_end is None:
            	y_end = num_y
            if z_end is None:
            	z_end = num_z

            proj_slc = slice(z_start, z_end, z_step)
            slices_slc = slice(y_start, y_end, y_step)
            pixel_slc = slice(x_start, x_end, x_step)

            if (array_name == "/exchange/theta"):
                # read the theta data
		data = f[array_name][proj_slc, ]
                # add a check that data is not None
                if data is None:
                    raise ValueError(_no_data_err.format(file=file_name, tag=array_name))
            else:
                # read the data
		data = f[array_name][proj_slc, slices_slc, pixel_slc]
                if data is None:
                    raise ValueError(_no_data_err.format(file=file_name, tag=array_name))
        return data

    def _dset_read(self, f_in, dset_name, slice_list):
        """
        Helper function for reading data sets that might not exist with arbitrary slices

        Parameters
        ----------
        f_in : h5py.Group
           Open file or group

        dset_name : str
           name of dataset to try to read

        slice_list : list or tuple
           slice object to use slicing the data set.  length needs to math
           the number of dimensions
        """
        # try to read the data
        try:
            out_data = f_in[dset_name][slice_list]
        # if KeyError is raised (because the data set does not exist)
        except KeyError:
            # set data to None
            out_data = None

        # return the data
        return out_data

    _no_data_err = "{file} does not contain {tag}"
