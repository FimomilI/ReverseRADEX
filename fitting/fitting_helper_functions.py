#!/usr/bin/env python3


# module imports
from numpy import (
    inf,
    log,
    pi
)
from numpy import sum as np_sum
from spectralradex.radex import run


class AlgorithmHelpers:
    def __init__(self,
                 observed_line_strengths,
                 observed_line_strengths_uncertainties,
                 unit_key,
                 bounds_low,
                 bounds_upp,
                 constant_parameters,
                 matching_lines,
                 fit_parameters_names):
        """constant variables/parameters required by the fitting
        algorithms but not necessarily able to be passed through outright.

        Args:
            observed_line_strengths (numpy.array[float]): observed line
            strengths obtained from the user supplied data file,
            units => T_R (K) -OR- FLUX (K*km/s) -OR- FLUX (erg/cm2/s). To
            be used in "log_likelihood()".
            
            observed_line_strengths_uncertainties (numpy.array[float]):
            observed line strengths uncertainties obtained from the user
            supplied data file,
            units => T_R (K) -OR- FLUX (K*km/s) -OR- FLUX (erg/cm2/s). To
            be used in "log_likelihood()".
            
            unit_key (str): string of what units the user supplied data
            consists of => T_R (K) -OR- FLUX (K*km/s) -OR- FLUX (erg/cm2/s).
            To be used in "RADEX_model()" as a "key" to slice SpectralRadex
            output.
            
            bounds_low (numpy.array[float]): lower bounds of all parameters
            to be fit => [par_1_low, par_2_low, ..., par_n_low], to be used
            in the prior calculation. To be used in "log_prior()".
            
            bounds_upp (numpy.array[float]): upper bounds of all parameters
            to be fit => [par_1_upp, par_2_upp, ..., par_n_upp], to be used
            in the prior calculation. To be used in "log_prior()".
            
            constant_parameters (dict): all parameters not (able to) fit
            stored in a dictionary, as SpectralRadex takes a dictionary
            as input. To be used in "RADEX_model()".
            
            matching_lines (numpy.array[bool]): array of booleans
            indicating which lines of the molecular file and SpectralRadex
            output are present in the user supplied data file, and can thus
            be compared. True if present, False if not present. To be used
            in "RADEX_model()" to cut the output.
            
            fit_parameters_names (list[str]): names, recognized by
            SpectralRadex, of parameters to be fit. To be used in
            "RADEX_model()".
            

        Retrun:
            None
        """
        
        self.y_obs                 = observed_line_strengths
        self.y_err                 = observed_line_strengths_uncertainties
        self.unit_key              = unit_key
        self.bounds_low            = bounds_low
        self.bounds_upp            = bounds_upp
        self.parameters            = constant_parameters
        self.matching_lines        = matching_lines
        self.fit_parameters_names  = fit_parameters_names
        
        return
        

    def RADEX_model(self, fit_parameters_values):
        """Calculates a RADEX model.

        Args:
            fit_parameters_values (nd.array): contains the parameter values
            of the parameters to be fit.
            

        Returns:
            nd.array: RADEX line strength output for matching lines.
        """
        
        variable_parameters = {
            variable_parameter_name:variable_parameter_value
            for variable_parameter_name, variable_parameter_value
            in zip(self.fit_parameters_names, 10.0**fit_parameters_values)
        }

        self.parameters.update(variable_parameters)

        # NOTE: if I use this to cut the output (for performance?), then
        # "output_matching_observation" has to be reworked as well since it
        # expects the full output.
        # output_limit = (
        #     self.matching_line_indeces[0] + self.matching_line_indeces[-1] + 1
        # )
        radex_output = run(self.parameters)#.head(output_limit)

        # cut (Spectral)RADEX output to match the user observed 
        # lines, provided in the datafile.
        output_matching_observation = radex_output.loc[
            self.matching_lines, self.unit_key
        ].to_numpy()

        return output_matching_observation


### MCMC functions only ###

    # FIXME: optimize this for speed? define a residuals function?
    def log_likelihood(self, fit_parameters_values):
        """logarithm of the likelihood distribution over datasets
        for the RADEX model.

        Args:
            fit_parameters_values (numpy array): values of the variable
            parameters to be fit in the MCMC algorithm.
        

        Returns:
            float: logarithm of the likelihood distribution.
        """
        
        y_RADEX = self.RADEX_model(fit_parameters_values)
        
        return - 0.5 * (log(2 * pi) + np_sum(
            2 * log(self.y_err) + ( (self.y_obs - y_RADEX) / self.y_err )**2
            )
        )


    def log_prior(self, fit_parameters_values):
        """logarithm of the uniform prior that solely checks if the
        walkers from the MCMC chain are within the supplied limits.

        Args:
            fit_parameters_values (numpy array): values of the variable
            parameters to be fit in the MCMC algorithm.
            

        Returns:
            float: "-inf" (unlikely to be true a.k.a. outside limits) or
            "0.0" within limits (possibly true parameter values).
        """
        
        check = (
            (fit_parameters_values >= self.bounds_low) ==
            (fit_parameters_values <= self.bounds_upp)
        )
        
        # check if any of the parameters are outside specified bounds.
        if False in check:
            return -inf
        else:
            return 0.0
        
        return


    def log_probability(self, fit_parameters_values):
        """the logarithm of the probability distribution for the
        parameter uncertainty estimation using MCMC to sample the
        parameters.
        
        Args:
            fit_parameters_values (numpy array): values of the variable
            parameters to be fit in the MCMC algorithm.
            

        Returns:
            float: logarithm of the probability distribution.
        """
        
        logprior = self.log_prior(fit_parameters_values)
        if logprior != 0.0:
            return -inf
        else:
            return logprior + self.log_likelihood(fit_parameters_values)

        return

### MCMC functions only ###