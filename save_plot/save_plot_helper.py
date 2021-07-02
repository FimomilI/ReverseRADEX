#!/usr/bin/env python3

#module imports
from spectralradex.radex import run
from numpy import array


def RADEX_model_plot(fit_parameter_names, parameters,
                     fit_parameters_values):
    """calculate RADEX model.

    Args:
        fit_parameter_names (list): list of names of parameters to fit.
        
        parameters (dict): constants.
        
        fit_parameters_values (array/list): fitted parameters' values.
        

    Returns:
        pd.DataFrame: full RADEX output + for which input parameters.
    """
    
    variable_parameters = {
        variable_parameter_name:variable_parameter_value
        for variable_parameter_name, variable_parameter_value
        in zip(fit_parameter_names, 10.0**array(fit_parameters_values))
    }

    parameters.update(variable_parameters)
    parameters['fmin']=0
    parameters['fmax']=3e7

    radex_output = run(parameters)
    
    return radex_output