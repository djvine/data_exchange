# -*- coding: utf-8 -*-
"""
.. module:: convert_CHESS.py
   :platform: Unix
   :synopsis: Convert CHESS TIFF files in data exchange.

.. moduleauthor:: Francesco De Carlo <decarlof@gmail.com>


""" 

import dataexchange.xtomo.xtomo_importer as dx
import dataexchange.xtomo.xtomo_exporter as ex

def main():

    file_name = '/local/dataraid/databank/CHESS/scan1/scan1_.tiff'
    dark_file_name = '/local/dataraid/databank/CHESS/scan1/scan1_dark_.tiff'
    white_file_name = '/local/dataraid/databank/CHESS/scan1/scan1_white_.tiff'

    hdf5_file_name = '/local/dataraid/databank/dataExchange/microCT/CHESS_02.h5'
    sample_name = 'Dummy'

    projections_start = 1
    projections_end = 361
    white_start = 0
    white_end = 1
    white_step = 1
    dark_start = 0
    dark_end = 1
    dark_step = 1


    # set to convert slices between slices_start and slices_end
    # if omitted all data set will be converted   
    slices_start = 400    
    slices_end = 405    

    mydata = dx.Import()
    # Read series of images
    data, white, dark, theta = mydata.series_of_images(file_name,
                                                       projections_start = projections_start,
                                                       projections_end = projections_end,
                                                       slices_start = slices_start,
                                                       slices_end = slices_end,
                                                       sample_name = sample_name,
                                                       projections_digits = 3,
                                                       projections_zeros = True,
                                                       log='INFO'
                                                    )    
##    mydata = ex.Export()
##    # Create minimal data exchange hdf5 file
##    mydata.xtomo_exchange(data = data,
##                          data_white = white,
##                          data_dark = dark,
##                          theta = theta,
##                          hdf5_file_name = hdf5_file_name,
##                          data_exchange_type = 'tomography_raw_projections'
##                          )

if __name__ == "__main__":
    main()

