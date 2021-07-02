#!/usr/bin/env python3

# module imports
from emcee.moves import (
    DESnookerMove,
    StretchMove,
    DEMove,
)
from emcee import EnsembleSampler
from multiprocessing import Pool, cpu_count
from numpy.random import randn


# required/suggested by emcee when using automatic parallelization done by
# numpy using MKL linear algebra for instance to disable it and let
# other implementations like Pool in this case take care of parallelization.
# see https://emcee.readthedocs.io/en/stable/tutorials/parallel
import os
os.environ["OMP_NUM_THREADS"] = "1"


# FIXME: set walkers as multiple of cpu_count()?
def run_monte_carlo(initial_parameters,
                    log_probability_function,
                    number_of_walkers=35,
                    number_of_steps=500,
                    number_of_burnin_steps=100,
                    number_of_walker_steps=200,
                    core_count=cpu_count()):
    """
    Args:
        initial_parameters (nd.array): initial parameters obtained by prior
        algorithms (grid search --> LM) in the chain.
        
        log_probability_function (function): logarithm (base10) of posterior.
                
        number_of_walkers (int): number of walkers. Defaults to 35.
        
        number_of_steps (int): number of steps. Defaults to 500.
        
        number_of_burnin_steps (int): number of burnin steps. Defaults to 100.
        
        number_of_walker_steps (int): number of walker steps. Defaults to 200.
        
        core_count (int): number of processors. Defaults to cpu_count().
        

    Returns:
        EnsambleSampler, int: emcee sampler object and number of parameters.
    """

    # Initialize the walkers in a Gaussian "ball" around the best initial
    # parameter estimates found by prior algorithms in the chain.
    pos = initial_parameters + 1e-3 * randn(number_of_walkers,
                                            initial_parameters.shape[0])
    nwalkers, ndim = pos.shape

    # run the MCMC algorithm.
    with Pool(processes=core_count) as pool:
        # FIXME: figure out the best set of moves for all molecules?
        sampler = EnsembleSampler(
            nwalkers, ndim, log_probability_function, pool=pool,
            moves=[(StretchMove(a=3), 0.7),
                   (DEMove(), 0.2),
                   (DESnookerMove(), 0.1),]
        )
        
        sampler.run_mcmc(pos, number_of_steps, progress=True)
        
        # FIXME: separate burnin and uncertainty sampling?
        # # calculate burnin chain.
        # idk = sampler.run_mcmc(pos, number_of_burnin_steps, progress=True)

        # # calculate walker (uncertainties?) chain.
        # sampler.run_mcmc(idk[???], number_of_walker_steps, progress=True)
    
    return sampler, ndim

