_test# -*- coding: utf-8 -*-
"""
.. module:: convert_Elettra.py
   :platform: Unix
   :synopsis: Convert Elettra Synchrotron facility, 12bit tiff compressed data LZV method, c files in data exchange.

.. moduleauthor:: Francesco De Carlo <decarlof@gmail.com>


""" 

import dataexchange.xtomo.xtomo_importer as dx
import dataexchange.xtomo.xtomo_exporter as ex

def main():

    file_name = '/local/dataraid/databank/Elettra/Volcanic_rock/tomo_.tif'
    dark_file_name = '/local/dataraid/databank/Elettra/Volcanic_rock/dark_.tif'
    white_file_name = '/local/dataraid/databank/Elettra/Volcanic_rock/flat_.tif'

    hdf5_file_name = '/local/dataraid/databank/dataExchange/microCT/Elettra_test.h5'

    projections_start = 1
    projections_end = 1441
    white_start = 1
    white_end = 11
    white_step = 1
    dark_start = 1
    dark_end = 11
    dark_step = 1
    
    sample_name = 'Volcanic_rock'

    # set to convert slices between slices_start and slices_end
    # if omitted all data set will be converted   
    slices_start = 150    
    slices_end = 154    

    mydata = dx.Import()
    # Read series of images
    data, white, dark, theta = mydata.series_of_images(file_name,
                                                       projections_start = projections_start,
                                                       projections_end = projections_end,
                                                       projections_digits = 4,
                                                       slices_start = slices_start,
                                                       slices_end = slices_end,
                                                       white_file_name = white_file_name,
                                                       white_start = white_start,
                                                       white_end = white_end,
                                                       white_step = white_step,
                                                       dark_file_name = dark_file_name,
                                                       dark_start = dark_start,
                                                       dark_end = dark_end,
                                                       dark_step = dark_step,
                                                       data_type =  'compressed_tiff', # comment this line if regular tiff
                                                       projections_zeros = True,
                                                       white_zeros = False,
                                                       dark_zeros = False,
                                                       sample_name = sample_name,
                                                       log='INFO'
                                                       )
    mydata = ex.Export()
    # Create minimal data exchange hdf5 file
    mydata.xtomo_exchange(data = data,
                          data_white = white,
                          data_dark = dark,
                          theta = theta,
                          hdf5_file_name = hdf5_file_name,
                          data_exchange_type = 'tomography_raw_projections'
                          )

if __name__ == "__main__":
    main()

