#!/usr/bin/env python3

# module import.
from scipy.optimize import least_squares


def run_levenberg_marquardt(parameter_estimates, model, y_obs, y_err):
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
        
        y_RADEX = model(parameters_to_optimize)
        if y_err.all() == 1:
            return y_RADEX - y_obs
        else:
            return (y_RADEX - y_obs) / y_err

        return


    ls_solution = least_squares(residuals, parameter_estimates, method='lm',
                                ftol=1e-10, xtol=1e-10, gtol=1e-10,)
    
    return ls_solution.x