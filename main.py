#!/usr/bin/env python3
#%% imports
from configparser import ConfigParser
from datetime import datetime, timedelta
from os import getcwd
from pathlib import Path
from time import time
import argparse

from numpy import append, array, full, log10

from fitting import (AlgorithmHelpers, find_initial_parameter_guesses,
                     run_levenberg_marquardt, run_monte_carlo)
from save_plot import Plotting, SaveResults
from user_input import (ConstantParamaters, DataRetrieval,
                        VariableParamters,
                        yay_or_nay)

input_constant = ConstantParamaters()
input_variable = VariableParamters()
data_retrieval = DataRetrieval()


#%% Read input from config.ini or ask for user input from terminal
parser = argparse.ArgumentParser(
    prog='Reverse RADEX',
    description='ReverseRADEX is a tool to quickly gauge the physical conditions in a gas cloud from line spectra.',
    epilog=''
)
parser.add_argument('-config', default=None)
args = parser.parse_args()


if args.config is not None:
    config = ConfigParser()
    config.read('config.ini')

    paths     = 'PATHS'
    constants = 'CONSTANT_PARAMETERS'
    variables = 'VARIABLE_PARAMETERS'

    # file locations.
    user_molfile = eval(config[paths]['MolecularFile'])
    user_datfile = eval(config[paths]['SpectraFile'])
    print(user_molfile, user_datfile)

    # constant parameters.
    Tbg             = eval(config[constants]['BackgroundTemperature'])
    dv              = eval(config[constants]['LineWidth'])
    geom, geom_name = eval(config[constants]['Geometry'])

    # variable parameters.
    temp_kin = eval(config[variables]['Tkin'])
    coldens  = eval(config[variables]['Coldens'])
    voldens  = eval(config[variables]['Voldens'])
else:  #### Catch user input from terminal ####
    user_molfile = input_constant.molfile_input()
    user_datfile = input_constant.datafile_input()

    # constant parameters.
    Tbg             = input_constant.background_radiation_input()
    dv              = input_constant.line_width_input()
    geom, geom_name = input_constant.geometry_input()

    # variable parameters.
    temp_kin = input_variable.kinetic_temperature_input()
    coldens  = input_variable.column_density_input()
    voldens  = input_variable.collision_densities_input()
#### Catch user input from terminal ####

# (matching) frequencies with molfile.
freq_indices = data_retrieval.get_molfile_frequency_index(
    user_datfile, user_molfile
)
freq = data_retrieval.get_frequencies(freq_indices, user_molfile)
user_mol_frequencies, freq_min, freq_max, number_of_lines_total = freq
freq_range = (freq_min, freq_max)

# checking for units and uncertainties.
units = data_retrieval.get_user_units(user_datfile)
uncertainties = data_retrieval.uncertainties_included(user_datfile)
(y_observed, y_uncertainties) = data_retrieval.line_strengths(
    user_datfile, uncertainties
)


#%% # printing the chosen settings for user to check.
print(f"\n\nSelected molfile path              : '{user_molfile}'")
print(f"Selected datafile path             : '{user_datfile}'")
print(f"Selected line strength units       : {units}")
print(f"uncertainties included             : {uncertainties}")
print("\n\n[name of parameter, parameter value, (lower bound, upper" +
      " bound), fit parameter?]")
print('If a parameter is fit, "parameter value" is a dummy number and ' +
      'can be ignored.\nIf not fit, the boundaries are dummy numbers.\n' +
      "0.0 just indicates SpectralRadex to not use this collision " +
      "partner.\n")
print(f"Selected minimum and maximum \n" +
      f"kinetic gas cloud temperature      : {temp_kin} K")
print(f"Selected background radiation field: {Tbg} K")
print(f"Selected minimum and maximum \n" +
      f"column densities                   : {coldens} cm^-2")


constant_parameters = {
    'tbg':Tbg, 'fmin':0, 'fmax':30_000_000, 'linewidth':dv,
    'geometry':geom, 'molfile':user_molfile
}

# handeling the kinetic temperatrue and column density.
lim_low = array([])
lim_upp = array([])
tkin_cd = [temp_kin, coldens]
lims_to_save = {}
for parameter in tkin_cd:
    prm_name, prm_value, prm_bounds, prm_fit = parameter
    if prm_fit == True:
        prm_low, prm_upp = prm_bounds
        lim_low = append(lim_low, log10(prm_low))
        lim_upp = append(lim_upp, log10(prm_upp))
        lims_to_save[prm_name] = (lim_low[-1], lim_upp[-1])
    else:
        constant_parameters[prm_name] = prm_value

# handeling the collision partners (volume densities).
str_voldens = "Selected volume densities [cm^-3],  "
print(str_voldens)
vol_dens_summary = []
min_max = 'min_max'
for collision_partner in voldens:
    if collision_partner != min_max:
        blank = ''.ljust(len(str_voldens) -
                         len(collision_partner) - 1) + ":"
        param_value, param_fit = voldens[collision_partner]
        voldens_min, voldens_max = voldens[min_max]
        vol_dens_summary += [[collision_partner, param_value,
                              (voldens_min, voldens_max), param_fit]]
        print(f"{collision_partner}" + blank +
              f" {vol_dens_summary[-1]}")
        if param_fit == False:
            constant_parameters[collision_partner] = param_value
        else:
            lim_low = append(lim_low, log10(voldens_min))
            lim_upp = append(lim_upp, log10(voldens_max))
            lims_to_save[collision_partner] = (lim_low[-1], lim_upp[-1])

# printing remaining input.
print(f"Selected line width                : {dv} km/s")
print(f"Selected minimum and maximum \n" +
      f"frequency                          : {freq_range} GHz")
print(f"Selected geometry                  : {geom_name}")


# check if any of the parameters is set to be fit.
if lim_low.shape[0] == 0:
    raise AssertionError("No parameter is set to be fit.")
else:  # set bounds for Least-Squares algorithm
    bounds = (lim_low, lim_upp)

# check if more data is available than parameters to fit.
# getting the names of the parameters to be fit, the order is important.
all_parameter_names = ['molfile', 'tkin', 'cdmol', 'tbg', 'h2', 'p-h2',
                       'o-h2', 'e-', 'h', 'he', 'h+', 'fmin', 'fmax',
                       'linewidth', 'geometry']
fit_parameters_names = []
for parameter_name in all_parameter_names:
    if parameter_name not in constant_parameters.keys():
        fit_parameters_names += [parameter_name]

len_data     = len(y_observed)
len_fit_prms = len(fit_parameters_names)
if (len_data > len_fit_prms) != True:
    raise AssertionError(f"{len_data} observed data points is not "
                         f"enough data to fit {len_fit_prms} parameters" +
                         ". Need: 'data > parameters + 1'.")

# prompt user to either continue to the fitting process or terminate.
user_prms_check = yay_or_nay("\nContinue to the fitting process? (y/n) ")
if user_prms_check == '' or user_prms_check == True:
    pass
else:
    raise KeyboardInterrupt("User terminated the program.")



#%% # select indices of observed frequencies
# since the frequency range is used to limit the radex output, the
# indices have to be shifted to accommodate for that (for instance, the
# range might start at 300 GHz while lines exist < 300 GHz. Therefore, the
# index needs to be shifted).
matching_index = list(map(lambda add: add - freq_indices[0], freq_indices))

# create an index array to be used for cutting the SpectralRadex output
# to match the spectral lines present in the user supplied data file.
matching_lines = full(number_of_lines_total, False)
matching_lines[matching_index] = True


#%% ### start of main program ###
start_time = time()

#### global parameter search ####
print("\nEstimating initial parameters.")
# use the brute method global search to find initial estimates for
# paremeters to be fit.
cst_prms = [user_molfile, Tbg, dv, freq_min, freq_max, geom, units,
            matching_index, user_datfile, uncertainties]
global_parameter_estimates = find_initial_parameter_guesses(
    temp_kin, coldens, voldens, vol_dens_summary, cst_prms
)

grid_time = time()
grid_duration  = grid_time - start_time
grid_duration_HHMMSS = str(timedelta(seconds=grid_duration)).rpartition('.')[0]
print(f"Time elapsed: {grid_duration_HHMMSS}")
print("Global parameter estimates resulting from brute " +
      "(grid search) method:")
for name, value in zip(fit_parameters_names, global_parameter_estimates):
    print(f"log10({name}): {value:.5f}")


#%% #### setting up Levenberg-Marquardt and MCMC parameters ####
alg_help = AlgorithmHelpers(
    y_observed,
    y_uncertainties,
    units,
    lim_low,
    lim_upp,
    constant_parameters,
    matching_lines,
    fit_parameters_names
)


#%% #### Levenberg-Marquardt least squares to refine parameter estimates ####
print("\nRefining parameter estimates.")
initial_parameters = run_levenberg_marquardt(global_parameter_estimates,
                                             alg_help.RADEX_model,
                                             y_observed,
                                             y_uncertainties,
                                             bounds)

LM_time = time()
LM_duration  = LM_time - start_time
LM_duration_HHMMSS = str(timedelta(seconds=LM_duration)).rpartition('.')[0]
print(f"Time elapsed: {LM_duration_HHMMSS}")
print("Refined parameter estimates resulting from Levenberg-Marquardt:")
for name, value in zip(fit_parameters_names, initial_parameters):
    print(f"log10({name}): {value:.5f}")


#%% #### MCMC for uncertainty estimates ####
N = 500  # number of steps the MCMC algorithm takes.
print("\nRunning MCMC for uncertainty estimates,")
MCMC_output, ndim = run_monte_carlo(initial_parameters,
                                    alg_help.log_probability,
                                    number_of_steps=N)


#%% ### end of main program ###
end_time = time()
duration = end_time - start_time
duration_HH_MM_SS = str(timedelta(seconds=duration)).rpartition('.')[0]
print(f"\nRun time of main program: {duration_HH_MM_SS}.")


#%% ##### plotting and saving of results #####
date_time = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
# FIXME: add filename of molecule + observations to output folder? (might become to long if the date_time is kept as well?)
# create output directory.
cwd         = getcwd()
output_path = cwd + f'/output/{date_time}'
Path(output_path).mkdir(parents=True)


### saving ###
saving = SaveResults(
    MCMC_output,
    output_path,
    constant_parameters,
    fit_parameters_names
)

# saving MCMC ensamble.
saving.save_MCMC_sampler()

# saving RADEX.csv output and obtaining parameter medians.
prms_50s, prms_MAP = saving.RADEX_for_optimal_parameters(
    user_datfile, user_mol_frequencies, y_observed, y_uncertainties,
    freq_indices, units, lims_to_save
)
### saving ###


### plotting ###
plot = Plotting(
    MCMC_output,
    output_path,
    prms_50s,
    prms_MAP,
    fit_parameters_names
)

# Plotting and saving the corner plot.
plot.plot_corner()

# Plotting the molecular spectrum.
plot.plot_spectrum(
    units, y_observed, y_uncertainties, constant_parameters,
    user_mol_frequencies
)
### plotting ###


print(f"\nResults saved to {output_path}.\n")


# %%
