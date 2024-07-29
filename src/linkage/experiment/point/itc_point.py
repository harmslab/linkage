
from .experimental_point import ExperimentalPoint

import numpy as np

class ITCPoint(ExperimentalPoint):
    """
    Class holds experimental data for an individual ITC experimental data point
    and how it links to the thermodynamic model. 
    """

    def __init__(self,
                 idx,
                 expt_idx,
                 obs_key,
                 micro_array,
                 macro_array,
                 meas_vol_dilution,
                 dh_param_start_idx,
                 dh_param_end_idx,
                 dh_sign,
                 dh_product_mask):
        """
        Initialize an ITC data point. 
        
        Parameters
        ----------
        idx : int
            index of point in the experimental array
        expt_idx : int
            index of the experiment itself (allowing multiple experiments)
        obs_key : str
            key pointing to observable from the experiment
        micro_array : np.ndarray (float)
            array holding concentrations of all microscopic species, calculated
            elsewhere
        macro_array : np.ndarray (float)
            array holding concentrations of all macroscopic species, calculated
            elsewhere
        meas_vol_dilution : float
            how much this shot diluted the measurement volume of the cell. This
            is calculated using the "titrator" function and corresponds to 
            (1 - v/V) where v is the injection volume and V is the cell volume
        dh_param_start_idx : int
            index of first enthalpy parameter in guesses array
        dh_param_end_idx : int
            index of last enthalpy parameter in guesses array
        dh_sign : list-like
            list of enthalpy signs (1 for forward, -1 for reverse) for each 
            reaction
        dh_product_mask : list-like
            list of boolean masks for pulling out products when calcuating 
            enthalpy changes
        """
        
        super().__init__(idx=idx,
                         expt_idx=expt_idx,
                         obs_key=obs_key,
                         micro_array=micro_array,
                         macro_array=macro_array)
        
        self._meas_vol_dilution = meas_vol_dilution
        self._dh_param_start_idx = dh_param_start_idx
        self._dh_param_end_idx = dh_param_end_idx
        self._dh_sign = dh_sign
        self._dh_product_mask = dh_product_mask
        
        
    def calc_value(self,parameters,*args,**kwargs):
        """
        Calculate the heat for this shot given the current estimated
        concentration changes and enthalpy parameters. *args and **kwargs are
        ignored. 

        Parameters
        ----------
        parameters : np.ndarray (float)
            fit parameters (guesses array)
        """

        dh_array = parameters[self._dh_param_start_idx:self._dh_param_end_idx]
    
        total_heat = 0.0
        for i in range(len(dh_array)):

            C_after  = self._micro_array[self._idx,self._dh_product_mask[i]]
            C_before = self._micro_array[self._idx-1,self._dh_product_mask[i]]
            dC = np.mean(C_after - C_before*self._meas_vol_dilution)

            total_heat += dh_array[i]*self._dh_sign[i]*dC
        
        
        return total_heat