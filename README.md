**Dependicies**: =>Python3.6, NumPy, SciPy, Pandas, Matplotlib, emcee, Corner, SpectralRadex

**OS**: tested on Linux but should be supported on Windows (likely dependents on SpectralRadex, which claims OS independence).

**How to run**: run main.py or main.ipynb if you prefer not to use a terminal. Pre-applied settings are present in main.ipynb (3rd cell) and _datfile.dat_ is the observed data file with a header (the first line starting with \#) indicating what units are used (1: T$_R$ [K], 2: $\mathcal{F}$ [K km s$^{−1}$], 3: $\mathcal{F}$ [erg cm$^{−2}$ s$^{−1}$]. The first column contains the frequencies in GHz, the 2nd column indicates the line strengths in terms of the specified units in the header, and the last column contains the uncertainties (leave blank if no uncertainties).
