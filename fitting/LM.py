#!/usr/bin/env python3

# module import.
from scipy.optimize import least_squares
from numpy import finfo, float64


# FIXME: https://rstudio-pubs-static.s3.amazonaws.com/226794_fdae25636b9b484896930dba386356ae.html make sure to use proper scaling when fitting?
def run_levenberg_marquardt(
        parameter_estimates,
        model,
        y_obs,
        y_err,
        parameter_bounds
    ):
    """run the Levenberg-Marquardt least squares algorithm on the RADEX
    model for the initial parameter estimates supplied by the global
    search algorithm. The least squares algorithm is used to refine the
    estimates of the minimum found by the global search algorithm, after
    which said parameters will be subject to an MCMC run for uncertainty
    estimates.

    Args:
        parameter_estimates (numpy.array): parameter estimates
        obtained via the global search algorithm.
        
        model (function): RADEX model calculated with SpectralRadex.
        
        y_obs (numpy.array): line strengths from the user supplied data
        file to be used in calculating the residuals.
        
        y_err (numpy.array): line strength uncertaintiesfrom the user
        supplied data file to be used in calculating the residuals.


    Return:
        numpy.array: the refined parameter estimates to be subject to
        an MCMC run.
    """
    
    norm = y_obs.max()
    y_obs_norm = y_obs / norm
    
    def residuals(parameters_to_optimize):
        """a function to calculate the residuals of SpectralRadex
        output compared with the observed data from the user supplied
        data file.

        Args:
            parameters_to_optimize (numpy.array): parameter estimates
            obtained via the global search algorithm.
            

        Returns:
            numpy.array: the residuals for the RADEX model, either with
            the inclusion of uncertainties or not.
        """
        
        y_RADEX_normalised = model(parameters_to_optimize) / norm
        if y_err.all() == 1:
            return y_RADEX_normalised - y_obs_norm
        else:
            return (y_RADEX_normalised - y_obs_norm) / y_err

        return

    # FIXME: I don't actually know what halve of the parameters I passed
    # here really do so start from a simpler fitting again when I know the
    # initial conditions are actually good (fix global search first). right
    # now it is still to susceptible to local minima, even though the MCMC
    # uncertainty estimate step after this is pretty good at finding the
    # "true" solution.
    # method='trf' seems fine though since 'lm' does not handle bounds.
    
    machine_epsilon10 = 1e4*finfo(float64).eps
    ls_solution = least_squares(
        residuals, parameter_estimates, method='trf', loss='cauchy',
        f_scale=0.17, bounds=parameter_bounds, ftol=machine_epsilon10,
        gtol=machine_epsilon10, xtol=machine_epsilon10, verbose=2
    )
    # ls_solution = least_squares(
    #     residuals, parameter_estimates, method='trf',
    #     bounds=parameter_bounds, verbose=2
    # )
    
    return ls_solution.x
