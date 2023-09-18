#!/usr/bin/env python3

#relative imports
from .save_plot_helper import RADEX_model_plot

# module imports
from matplotlib.pyplot import figure, show
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import randint
import warnings
import corner


class Plotting:
    def __init__(self,
                 sampler,
                 output_path,
                 parameter_50s,
                 fit_parameter_names):
        """class used for plotting.

        Args:            
            sampler (emcee:EnsembleSampler): MCMC parameter coordinates.
            
            output_path (str): output folder.

            parameter_50s (nd.array): MCMC parameter medians.
            
            fit_parameter_names (list): Names of fitted parameters.


        Returns:
            None
        """

        self.sampler             = sampler
        self.output_path         = output_path
        self.parameter_50s       = parameter_50s
        self.fit_parameter_names = fit_parameter_names

        # FIXME: put in the molecule name for column density.
        plot_names = {
            'tkin':r"log$_{10}$(T$_{\mathrm{kin}}$) [K]",
            'cdmol':r"log$_{10}$(N$_{\mathrm{mol}}$) [cm$^{-2}$]",
            'h2':r"log$_{10}$(H$_2$) [cm$^{-3}$]",
            'p-h2':r"log$_{10}$(p-H$_2$) [cm$^{-3}$]",
            'o-h2':r"log$_{10}$(o-H$_2$) [cm$^{-3}$]",
            'e-':r"log$_{10}$(e$^-$) [cm$^{-3}$]",
            'h':r"log$_{10}$(H) [cm$^{-3}$]",
            'he':r"log$_{10}$(He) [cm$^{-3}$]",
            'h+':r"log$_{10}$(H$^+$) [cm$^{-3}$]"
        }

        self.plot_labels = [plot_names[plot_name]
                            for plot_name
                            in self.fit_parameter_names]

        return


    def plot_corner(self):
        """Make and save a corner plot of the MCMC sampled posterior
        distributions of the parameters that are fit. both 2D contours
        between parameters and 1D distributions.


        Returns:
            None
        """
        flat_samples = self.sampler.get_chain(discard=100, flat=True)
        fig = corner.corner(
            flat_samples, labels=self.plot_labels, truths=self.parameter_50s,
            quantiles=(0.16, 0.84), levels=(1 - np.exp(-0.5),), smooth=True,
            label_kwargs={'fontsize':15}
        )

        plt.close(fig)
        fig.savefig(f'{self.output_path}/MCMC_corner_plot.png',
                    dpi=300, bbox_inches='tight')

        return


    def plot_spectrum(self,
                      unit_name,
                      line_strength_y,
                      line_strength_err,
                      constant_parameters,
                      frequencies):
        """plot the observed data points, as well as the RADEX model
        spectrum for the best estimates and an "uncertainty" interval
        using 100 random MCMC results.

        Args:
            unit_name (str): dict key of units selected by user.
            
            line_strength_y (nd.array): user line strenghts.
            
            line_strength_err (nd.array): user line strength uncertainties.
            
            constant_parameters (dict): RADEX input for SpectralRadex for
                                        the constant input.
            
            frequencies (nd.array): molfile frequencies matching user
                                    frequencies.


        Returns:
            None
        """

        unit_labels = {
            'T_R (K)':r'T$_R$ [K]',
            'FLUX (K*km/s)':r'F [K km s$^{-1}$}]',
            'FLUX (erg/cm2/s)':r'F [erg cm$^{-2}$ s$^{-1}$]'
        }

        fig   = figure(figsize=(15,10.5))
        frame = fig.add_subplot(1,1,1)

        
        # plot 100 randomly drawn RADEX models to showcase uncertainty
        # interval loosely.
        flat_samples = self.sampler.get_chain(discard=100, flat=True)
        inds = randint(len(flat_samples), size=100)
        for ind in inds:
            sample = flat_samples[ind]
            rnd_output = RADEX_model_plot(
                self.fit_parameter_names, constant_parameters, sample
            )
            rnd_freqs          = rnd_output['freq']
            rnd_line_strengths = rnd_output[unit_name]
            frame.scatter(rnd_freqs, rnd_line_strengths, color='#4daf4a',
                          alpha=0.1, marker='s')
        # FIXME: add to legend without dummy plot.
        # a dummy plot to add MCMC "uncertainty interval" to legend.
        frame.plot(frequencies[0], line_strength_y[0], color='#4daf4a',
                   marker='s', scalex=False, scaley=False, alpha=0.8,
                   zorder=0, label='MCMC uncertainty interval',
                   linestyle = 'None')


        # plot RADEX model for the optimal parameter estimates
        output_50 = RADEX_model_plot(
            self.fit_parameter_names, constant_parameters,
            self.parameter_50s
        )
        freq_50           = output_50['freq']
        line_strengths_50 = output_50[unit_name]
        frame.scatter(freq_50, line_strengths_50,
                      color='#ff7f00', marker='D',
                      label='RADEX optimal parameters', s=70)


        ## ignore UserWarning ##
        # The warning says "fmt" is redundant when "marker" is defined
        # (or vice versa?) but this does not seem to be the case.
        def usr():
            warnings.warn("user warning", UserWarning)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            usr()
            # plot observations.
            frame.errorbar(frequencies, line_strength_y,
                           yerr=line_strength_err,
                           marker='.', fmt=',', mew=3, ms=13, linewidth=1,
                           capsize=3, capthick=1, alpha=0.66,
                           color='dodgerblue', ecolor='black',
                           label='Observed data', zorder=10)
        ## ignore UserWarning ##
        

        # FIXME: make sure that this legend placement is sufficient
        # for every molecule?
        frame.legend(fontsize=16, fancybox=False, shadow=False, ncol=1,
                     frameon=False, loc='upper left',
                     bbox_to_anchor=(-0.01, 0.97275))
        frame.set_xlabel(r'$\nu$ [GHz]', fontsize=21)
        frame.set_ylabel(unit_labels[unit_name], fontsize=21)
        frame.yaxis.offsetText.set_fontsize(18)
        frame.set_axisbelow(True)
        frame.grid(True)
        frame.set_yscale('log')
        frame.set_ylim(
            line_strength_y.min()-5*line_strength_err[np.argmin(line_strength_y)],
            line_strength_y.max()+5*line_strength_err[np.argmax(line_strength_y)]
        )
        frame.set_xlim(min(frequencies)-100, max(frequencies)+100)

        frame.tick_params(axis='both', direction='in', which='major',
                          length=10, width=1, labelsize=18)
        
        fig.savefig(f'{self.output_path}/spectrum.png',
                    dpi=300, bbox_inches='tight')
        show()
        
        return