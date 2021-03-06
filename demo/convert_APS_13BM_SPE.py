"""
.. module:: convert_APS_13BM.py
   :platform: Unix
   :synopsis: Convert APS 13-BM SPE files in data exchange.

.. moduleauthor:: Francesco De Carlo <decarlof@gmail.com>


""" 

import dataexchange.xtomo.xtomo_importer as dx
import dataexchange.xtomo.xtomo_exporter as ex

def main():

    file_name = '/local/dataraid/databank/APS_13_BM/SPE/run2_soln1_2_.SPE'
    hdf5_file_name = '/local/dataraid/databank/dataExchange/microCT/APS_13_BM_test_07.h5'

    white_start = 1
    white_end = 8
    white_step = 2
    projections_start = 2
    projections_end = 7
    projections_step = 2

    # set to convert slices between slices_start and slices_end
    # if omitted all data set will be converted   
    slices_start = 100    
    slices_end = 104    

    mydata = dx.Import()
    # Read series of images
    data, white, dark, theta = mydata.series_of_images(file_name,
                                                       projections_start = projections_start,
                                                       projections_end = projections_end,
                                                       projections_step = projections_step,
                                                       slices_start = slices_start,
                                                       slices_end = slices_end,
                                                       white_start = white_start,
                                                       white_end = white_end,
                                                       white_step = white_step,
                                                       projections_zeros=False,
                                                       white_zeros=False,
                                                       dark_zeros=False,
                                                       data_type='spe',
                                                       sample_name = 'Stripe_Solder_Sample_Tip1',
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

