#!/usr/bin/env python3



# FIXME: this whole file should be rewritten pretty much, latent MAGIX
# code, long function, not utilizing pandas like in
# "fitting_helper_function.py", how parameters that are either fit or not
# are handeled, etc.
# pretty much make this function similar to LM.py or MCMC.py but above all,
# probably should look into the bees algorithm or pso algorithm or other
# global search algorithm besides grid search to combat parameter
# degeneracy.



#%%
# module imports
from numpy import (
    concatenate,
    geomspace,
    linspace,
    loadtxt,
    append,
    array,
    where,
    log10,
    full,
    ones,
    ix_
)
from spectralradex.radex import run_grid
from multiprocessing import cpu_count, Pool
import warnings


def data_file_extraction(user_data_file, uncertainty):
    """extract the line strength column (with uncertainties) from the
    user supplied data file. These uncertainties are only used for
    calculating the chi^2 values so the default uncertainties = 1 (or
    any other constant) since they have no effect then.

    Args:
        user_data_file (str): user supplied data file directory.
        
        uncertainty (str): uncertainties included ('yes' -OR- 'no')
        

    Returns:
        tuple: 1 numpy array with line strenghts and 1 numpy array
        with line strength uncertainties.
    """
    data = loadtxt(user_data_file).T
    if uncertainty == 'no':
        line_strenghts = data[1]
        return (line_strenghts, ones(line_strenghts.shape[0]))
    else:
        line_strenghts, line_strenght_uncertanties = data[1:]
        return (line_strenghts, line_strenght_uncertanties)

    return


# FIXME: use *args for y_err based on uncertainty?
def chi_squared(y_fit, y_obs, y_err, uncertainty):
    """calculate the chi^2 values between the user data file and the
    spectralRadex grid calculations (y_err as a default is equal to an
    array of ones).

    Args:
        y_fit (numpy array): the spectralRadex grid fit line strengths
        for all transition lines [T_R (K) -OR- FLUX (K*km/s) -OR-
        FLUX (erg/cm2/s)].
        
        y_obs (numpy array): the observed line strengths read from data
        file [T_R (K) -OR- FLUX (K*km/s) -OR- FLUX (erg/cm2/s)].
        
        y_err (numpy array): the observed line strength uncertainties
        read from data file [T_R (K) -OR- FLUX (K*km/s) -OR-
        FLUX (erg/cm2/s)].
        
        uncertainty (str): are uncertainties included ('yes', 'no').


    Returns:
        [numpy array]: chi_squared values
    """
    if uncertainty == 'no':
        return ( (y_obs - y_fit)**2 ).sum(axis=1)
    else:
        return ( ( (y_obs - y_fit) / y_err )**2 ).sum(axis=1)

    return


def find_initial_parameter_guesses(kinetic_temperature, column_density,
                                   voldens, volume_density,
                                   constant_parameters,
                                   core_count=cpu_count()):
    """calculate the initial parameter guesses to be used by MAGIX
    based on user supplied parameter fit information (bounds,
    fit=True/False, observed data). This is done with spectralRadex's
    grid running function that runs one (large) grid, from which the
    parameter values with the lowest chi2 are chosen as initial
    estimates. This global search method is not very optimized and is
    sometimes referred to as the "brute method". Alternatives
    would be the bees algorithm or particle swarm optimization amongst
    other.

    Args:
        summary = [name [str], value [float], (lim_low, lim_upp) [floats],
        fit (bool)]
        
        kinetic_temperature (list): summary of kinetic temperature.
        
        column_density (list): summary of column density.
        
        voldens (list): list of summaries of all collision partners.
        
        volume_density (list): list of summaries of all collision partners.
        
        constant_parameters (list): list of required constant parameters
        for spectralRadex and user data file information.
        

    Returns:
        list: list of lists of parameters that now contains the initial
        parameter guesses for the values to be written to "parameters.xml"
        for MAGIX.
    """
    _, Tkin_value, Tkin_limits, Tkin_fit = kinetic_temperature
    _, cd_value, cd_limits, cd_fit     = column_density
    (user_molfile, Tbg, dv, freq_min, freq_max, geom,
     units, matching_index, user_datfile,
     uncertainties) = constant_parameters


    # counting the number of parameters to fit (will later be used for
    # masking spectralRadex output when comparing to observational data
    # and when retreiving the best initial parameter guesses).
    # excluding the volume densities for now (the next for loop accounts
    # for those).
    parameters_to_fit = [Tkin_fit, cd_fit]
    number_of_parameters_to_fit = 0
    for fit in parameters_to_fit:
        if fit == True:
            number_of_parameters_to_fit += 1

    Tkin_min, Tkin_max       = Tkin_limits
    cd_min, cd_max           = cd_limits
    voldens_min, voldens_max = voldens['min_max']
    
    num_points_tkin = int((Tkin_max - Tkin_min) / 40)
    if num_points_tkin < 5:
        num_points_tkin = 5
    elif num_points_tkin > 30:
        num_points_tkin = 30

    num_points_cd = int(log10(cd_max) - log10(cd_min)) - 1
    if num_points_cd < 5:
        num_points_cd = 5

    # FIXME: what if multiple collision partners are fit, it will be a very
    # large grid and take a long time just to find initial parameters.
    num_points_voldens = int(log10(voldens_max) - log10(voldens_min)) + 3
    if num_points_voldens < 7:
        num_points_voldens = 7
    
    # TODO: if num_points_tkin + num_points_cd + num_points_voldens > 40?
    # than decrease it for all points to a more reasonable grid by limiting
    # the largest num_points_*** first, until the total < 40? again.
    # num_points_list = [num_points_tkin + num_points_cd + num_points_voldens]
    # if sum(num_points_list) > 50:
    #     sorted(num_points_list)
    

    # be sure to exclude the first and last point of the chosen limits
    # by taking endpoint=False and [1:] to exclude the starting point.
    if Tkin_fit == True:
        Tkin_grid = linspace(Tkin_min, Tkin_max,
                             num_points_tkin + 1, endpoint=False)[1:]
    else:
        Tkin_grid = Tkin_value

    if cd_fit == True:
        cd_grid = geomspace(cd_min, cd_max,
                            num_points_cd + 1, endpoint=False)[1:]
    else:
        cd_grid = cd_value


    grid_guess_parameters = {}
    for collision_partner in voldens:
        # exclude the volume density bounds
        if collision_partner != 'min_max':
            value, fit = voldens[collision_partner]
            if fit == False:
                grid_guess_parameters[collision_partner] = value
            else:
                number_of_parameters_to_fit += 1
                grid_guess_parameters[collision_partner] = geomspace(
                    voldens_min, voldens_max, num_points_voldens + 1,
                    endpoint=False
                )[1:]

    grid_guess_parameters['tkin']      = Tkin_grid
    grid_guess_parameters['cdmol']     = cd_grid
    grid_guess_parameters['molfile']   = user_molfile
    grid_guess_parameters['tbg']       = Tbg
    grid_guess_parameters['linewidth'] = dv
    grid_guess_parameters['fmin']      = freq_min
    grid_guess_parameters['fmax']      = freq_max
    grid_guess_parameters['geometry']  = geom
    # print(grid_guess_parameters)

    
    # FIXME: use psutil.cpu_count(logical=True) instead?
    pool = Pool(processes=core_count)

    grid_output_DataFrame = run_grid(grid_guess_parameters,
                                     target_value=units,
                                     pool=pool)
    # FIXME: instead of ".to_numpy()" use pandas dataframe namings for
    # columns instead? might make code clearer but speed should not
    # be an issue to begin with (see example in SpectralRadex code
    # or in LM.py/MCMC.py).
    grid_output = grid_output_DataFrame.to_numpy()

    # "number_of_parameters_to_fit" accounts for the variable parameters
    # used in the grid calculations (and also output) by spectralRadex
    # and thus in need of removal when compared to user data.
    grid_output_cut = grid_output[:,number_of_parameters_to_fit:]


    # only take the spectralRadex output for matching (observed) lines
    # taken from the data file.
    grid_output_to_compare = grid_output_cut[
        ix_(full(grid_output_cut.shape[0], True), matching_index)
    ]

    y_observed, y_uncertainties = data_file_extraction(user_datfile,
                                                       uncertainties)
    
    # using '[None,:]' to "match" the dimensionality of
    # 'grid_output_to_compare' and be able to easily vectorize the chi2
    # calculation.
    chi2 = chi_squared(grid_output_to_compare,
                       y_observed[None,:], y_uncertainties[None,:],
                       uncertainties)

    min_chi2_index = int(where(chi2 == chi2.min())[0][0])

    ## ignore UserWarning ##
    # user warning is that irrelevant columns have the same name.
    def usr():
        warnings.warn("user warning", UserWarning)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        usr()
        grid_output_dict = grid_output_DataFrame.to_dict()
    ## ignore UserWarning ##


    global_parameter_estimates = array([])
    if Tkin_fit == True:
        global_tkin = grid_output_dict['tkin'][min_chi2_index]
        global_parameter_estimates = append(
            global_parameter_estimates, log10(global_tkin)
        )
        
    if cd_fit == True:
        global_cd = grid_output_dict['cdmol'][min_chi2_index]
        global_parameter_estimates = append(
            global_parameter_estimates, log10(global_cd)
        )
        

    ## suppress deprecation warning ##
    def depr():
        warnings.warn("deprecated", DeprecationWarning)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        depr()
        # save the initial parameter guesses (vol_dens) to appropriate lists.
        for collision_partner in volume_density:
            col_partner_name, *_, col_partner_fit = collision_partner
            if col_partner_fit == True:
                collision_partner_index = int(
                    where(
                        array(volume_density).T[0] == col_partner_name
                        )[0][0]
                )
                volume_density[collision_partner_index][1] = (
                    grid_output_dict[col_partner_name][min_chi2_index]
                )
                global_vd = grid_output_dict[col_partner_name][min_chi2_index]
                global_parameter_estimates = append(
                    global_parameter_estimates, log10(global_vd)
                )
    ## suppress deprecation warning ##
    
    return global_parameter_estimates