# -*- coding: utf-8 -*-
"""
.. module:: import_tomoPy_APS_1ID.py
   :platform: Unix
   :synopsis: reconstruct APS 1-ID with TomoPy
   :INPUT
       series of tiff or data exchange 

.. moduleauthor:: Francesco De Carlo <decarlof@gmail.com>


""" 
# tomoPy: https://github.com/tomopy/tomopy
import tomopy 

# Data Exchange: https://github.com/data-exchange/data-exchange
import dataexchange.xtomo.xtomo_importer as dx

import re

def main():
    file_name = '/local/dataraid/databank/APS_1_ID/APS1ID_Cat4B_2/CAT4B_2_.tif'
    log_file = '/local/dataraid/databank/APS_1_ID/APS1ID_Cat4B_2/CAT4B_2_TomoStillScan.dat'

    hdf5_file_name = '/local/dataraid/databank/dataExchange/microCT/CAT4B_2_test_01.h5'

    #Read APS 1-ID log file data
    file = open(log_file, 'r')
    for line in file:
        linelist=line.split()
        if len(linelist)>1:
            if (linelist[0]=="First" and linelist[1]=="image"):
                projections_start = int(linelist[4])
            elif (linelist[0]=="Last" and linelist[1]=="image"):
                projections_end = int(linelist[4])
            elif (linelist[0]=="Dark" and linelist[1]=="field"):
                dark_start = int(linelist[6])
            elif (linelist[0]=="Number" and linelist[2]=="dark"):
                number_of_dark = int(linelist[5])
            elif (linelist[0]=="White" and linelist[1]=="field"):
                white_start = int(linelist[6])
            elif (linelist[0]=="Number" and linelist[2]=="white"):
                number_of_white = int(linelist[5])
    file.close()
    
    dark_end = dark_start + number_of_dark
    white_end = white_start + number_of_white

    # to fix a data collection looging bug ? 
    white_start = white_start + 1
    dark_start = dark_start +1
    projections_start = projections_start + 11
    projections_end = projections_end - 9
    
    
##    # these are correct per Peter discussion
##    projections_start = 943
##    projections_end = 1853
##    white_start = 1844
##    white_end = 1853
##    dark_start = 1854
##    dark_end = 1863

    print projections_start, projections_end
    print dark_start, dark_end
    print white_start, white_end
   
    # set to convert slices between slices_start and slices_end
    # if omitted all data set will be converted   
    slices_start = 1000    
    slices_end = 1004    

    mydata = dx.Import()
    # Read series of images
    data, white, dark, theta = mydata.series_of_images(file_name,
                                                       projections_start = projections_start,
                                                       projections_end = projections_end,
                                                       slices_start = slices_start,
                                                       slices_end = slices_end,
                                                       white_start = white_start,
                                                       white_end = white_end,
                                                       dark_start = dark_start,
                                                       dark_end = dark_end,
                                                       projections_digits = 6,
                                                       log='INFO'
                                                       )

##    # if you have already created a data exchange file using convert_SLS.py module,
##    # comment the call above and read the data set as data exchange 
##    # Read HDF5 file.
##    data, white, dark, theta = tomopy.xtomo_reader(hdf5_file_name,
##                                                   slices_start=0,
##                                                   slices_end=2)

    # TomoPy xtomo object creation and pipeline of methods.  
    d = tomopy.xtomo_dataset(log='debug')
    d.dataset(data, white, dark, theta)
    d.normalize()
    d.correct_drift()
    #d.optimize_center()
    #d.phase_retrieval()
    #d.correct_drift()
    d.center=1026.0
    d.gridrec()


    # Write to stack of TIFFs.
    tomopy.xtomo_writer(d.data_recon, 'tmp/APS_1ID_', axis=0)

if __name__ == "__main__":
    main()

