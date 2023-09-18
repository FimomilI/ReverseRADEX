#!/usr/bin/env python3


#relative imports
from .save_plot_helper import RADEX_model_plot

#module imports
from numpy import (
    percentile,
    savetxt,
    array,
    diff,
    sort,
    full,
    NaN
)
import numpy as np
from pandas import read_csv


class SaveResults:
    def __init__(self,
                 sampler,
                 output_path,
                 constant_parameters,
                 fit_parameters_names):
        """        
        Args:
            sampler (EnsambleSampler): emcee sampler object containing
            all MCMC sampler parameter coordinates.
            
            output_path (str): output directory.

            constant_parameters (dict): dictionary of the constant
            parameter inputs of SpectralRadex.
            
            fit_parameters_names (list): parameter names of parameters
            to be fit.


        Returns:
            None
        """

        self.sampler              = sampler
        self.output_path          = output_path
        self.constant_parameters  = constant_parameters
        self.fit_parameters_names = fit_parameters_names
        return
    
    
    # CRED: http://bebi103.caltech.edu.s3-website-us-east-1.amazonaws.com/2015/tutorials/l06_credible_regions.html
    def hpd(self, i, mass_frac):
        # """
        # Returns highest probability density region given by
        # a set of samples.

        # Parameters
        # ----------
        # trace : array
        #     1D array of MCMC samples for a single variable
        # mass_frac : float with 0 < mass_frac <= 1
        #     The fraction of the probability to be included in
        #     the HPD.  For example, `massfrac` = 0.95 gives a
        #     95% HPD.
            
        # Returns
        # -------
        # output : array, shape (2,)
        #     The bounds of the HPD
        # """
        
        trace = self.sampler.get_chain(discard=100, flat=True)[:,i]
        
        # Get sorted list
        d = np.sort(np.copy(trace))

        # Number of total samples taken
        n = len(trace)
        
        # Get number of samples that should be included in HPD
        n_samples = np.floor(mass_frac * n).astype(int)
        
        # Get width (in units of data) of all intervals with n_samples samples
        int_width = d[n_samples:] - d[:n-n_samples]
        
        # Pick out minimal interval
        min_int = np.argmin(int_width)
        
        # mode = self.sampler.get_chain(discard=100, flat=True) [np.argmax(self.sampler.flatlnprobability)][i]
        # FIXME: make sure this is actually the mode, it does not look correct
        # in the corner plot? as in, the "truth" line is not at the maximum of
        # the histogram?
        mode = self.sampler.get_chain(discard=100, flat=True) [np.argmax(self.sampler.get_log_prob(discard=100, flat=True))][i]
        
        # Return interval
        return np.array([d[min_int], mode, d[min_int+n_samples]])


    # FIXME: add log10(...) in string when outputting data values, instead
    # of assuming people will just understand that outright. + add units!!!
    def print_parameter_uncertainty_estimates(self,
                                              user_datfile,
                                              user_frequencies,
                                              limits):
        """prints and saves fit information.

        Args:
            user_datfile (str): observed user data file location.
            
            user_frequencies (list): observed user line frequencies.
            
            limits (dict): dictionary of the limits for fit parameters.
            

        Returns:
            list: parameter medians
        """
        
        parameter_50s = []
        print("\nParameter estimates and accompanying upper and "
              "lower uncertainties,")
        prms_sum_dir = f'{self.output_path}/parameters.txt'
        with open(prms_sum_dir, 'w') as prms_txt:
            prms_txt.write(
                'Data file used: ' +
                user_datfile +
                '\n'
            )
            prms_txt.write(
                'Line (frequencies [Hz]) used: ' +
                str(user_frequencies)[1:-1] +
                '\n'
            )
            for i, parameter_name in enumerate(self.constant_parameters):
                if parameter_name in self.fit_parameters_names:
                    prms_txt.write(
                        f"{parameter_name}'s parameter boundaries: " +
                        f'{limits[parameter_name]}\n'
                    )
                else:
                    prms_txt.write(
                        f'{parameter_name} = ' +
                        f'{self.constant_parameters[parameter_name]}\n'
                    )

            
            # header = f"Percental:   50%   |   16%   |   84%   "
            sigma = 0.68  # 1 standard deviation, although 95% seems more common with (MCMC) confidence intervals?
            header = f"{100*sigma}% confidence interval around mode"
            print(header)
            prms_txt.write('\n' + header)
            for i, parameter_name in enumerate(self.fit_parameters_names):
                # # obtaining the median and upper and lower uncertainties
                # # that enclose 1 sigma.
                # parameter_uncertainty_estimates = percentile(
                #     self.sampler.get_chain(discard=100, flat=True)[:, i],
                #     q=[16, 50, 84]
                # )
                # uncertainties = diff(parameter_uncertainty_estimates)
                
                # median = parameter_uncertainty_estimates[1]
                # prm_16, prm_84 = uncertainties
                
                # parameter_50s += [median]

                # parameter_summary = (
                #     f"log10({parameter_name})    : {median:.5f} | -" +
                #     f"{prm_16:.5f} | +{prm_84:.5f}"
                # )
                
                
                # FIXME / NOTE: this is no longer the median=50% nor 16%, 84%, unless it is a symetric gaussian?
                confidence = self.hpd(i, sigma)
                parameter_50s += [confidence[1]]
                lci, uci = diff(confidence)
                parameter_summary = (
                    f"log10({parameter_name})    : {parameter_50s[i]:.5f} | -" +
                    f"{lci:.5f} | +{uci:.5f}"
                )
                
                
                
                print(parameter_summary)
                prms_txt.write('\n' + parameter_summary)

        return parameter_50s


    def save_MCMC_sampler(self):
        """save emcee EnsembleSampler.flatchain object.
        """

        savetxt(
            f'{self.output_path}/sampler.dat',
            self.sampler.get_chain(flat=True),
            header=str(self.fit_parameters_names)[1:-1]
        )
        
        return


    def RADEX_for_optimal_parameters(self,
                                     user_datfile,
                                     user_frequencies,
                                     y_obs,
                                     y_err,
                                     matching_indices,
                                     units,
                                     limits):
        """saves RADEX.csv, which is a RADEX model output for
        the parameter medians estimated with the MCMC algorithm.
        Addintionally, the chi^2 for each observed line is
        calculated and saved as well.

        Args:
            user_datfile (str): user observed data file location.
            
            user_frequencies (list): user observed frequencies.
            
            y_obs (list): user observed line strengths.
            
            y_err (list): user observed line strengths uncertainties.
            
            matching_indices (list): incides that match the user
            observations with the RADEX output.
            
            units (str): dictunary key that indicates the units used
            in user_datfile.
            
            limits (dict): dictionary of the limits for fit parameters.
            

        Returns:
            list: parameter medians
        """

        # this is the only way the function below is called.
        params_50 = self.print_parameter_uncertainty_estimates(
            user_datfile, user_frequencies, limits
        )
        optimal_RADEX = RADEX_model_plot(
            self.fit_parameters_names, self.constant_parameters, params_50
        )


        # FIXME: calculate the proper reduced chi^2 of the total fit (not
        # this weird one of the individual lines (essentially just
        # residual squared)), and put that in parameters.txt?
        # # define to chi2 column to be added to RADEX.csv.
        # y_RADEX = optimal_RADEX.loc[matching_indices, units].to_numpy()
        # if y_err.all() == 1:
        #     chi2_calc = (y_obs - y_RADEX) ** 2
        # else:
        #     chi2_calc = ( (y_obs - y_RADEX) / y_err ) ** 2
        
        # chi2 = full(optimal_RADEX[units].shape[0], NaN)
        # chi2[matching_indices] = chi2_calc
                
        csv_path = f'{self.output_path}/RADEX.csv'
        # write RADEX output to csv.
        optimal_RADEX.to_csv(
            csv_path, sep=',', na_rep='', #float_format='%.5e'
        )
        # # read the RADEX output.
        # csv_file = read_csv(csv_path)
        # # add the chi2 values as the last column.
        # csv_file['chi^2'] = array(chi2)
        # # save the new RADEX .csv file.
        # csv_file.to_csv(
        #     csv_path, index=False, na_rep='not fit', float_format='%.5e'
        # )
        
        return params_50



    
        