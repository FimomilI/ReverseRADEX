<div id="header" align="center" style="border: 4px solid #ccc; border-radius: 50px; padding: .5em .5em;">
  <!-- add a banner image with text "ReverseRadex" or something? maybe an image of a spectrum? ALSO add badges for; version?, which python versions are supported, which platform/OS is supported ... -->
  <big style="font-size:42px;">ReverseRADEX</big>
  
  <br />

  [![pythonV](https://img.shields.io/badge/python-3.6+-blue?style=for-the-badge)](https://www.python.org) [![MIT](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](./LICENSE) ![development](https://img.shields.io/badge/development-inactive/sporadic-red?style=for-the-badge)
</div>

<br />

ReverseRADEX is a tool to quickly gauge the physical conditions in a gas cloud from line spectra. [RADEX](https://personal.sron.nl/~vdtak/radex/index.shtml) is a 1D non-LTE radiative transfer code that assumes a homogeneous isothermal gas cloud. Where the medium is described using the [escape probability formalism](https://www.aanda.org/articles/aa/full/2007/23/aa6820-06/aa6820-06.right.html#SECTION00033000000000000000 "Escape probability implementation in RADEX") to first order.

What ReverseRADEX offers:

- 
<!-- itemized key features?
- LAMDA file format
- Chain algorithm optimization
  - Fig 2?
- Parameter estimation + uncertainty budget (HPD?/HDI? and link to a wikipedia source or whatever on this to make clear what numbers are being reported!!!)
  - Parameter correlation
- ???
-->


<br />

RADEX was originally written in Fortran but implemented in ReverseRADEX via a python wrapper package, [GitHub/uclchem/SpectralRadex](https://github.com/uclchem/SpectralRadex). In addition to wrapping the source code, it was also modernized to introducing proper multiprocessing capabilities. \
The supported (file format for the) molecular data is maintained in the Leiden Atomic and Molecular Database, [LAMDA](https://home.strw.leidenuniv.nl/~moldata/).

Highlighted in Figure [1](#Figure1) is the benefit of ReverseRADEX over regular RADEX. It automates the optimization process of matching model spectra to observed line spectra.


<!-- AND what is being fit exactly (an SLED (various units)? see thesis again) -->


<div id="Figure1" align="center">

  ```mermaid
  %%{
    init:{
      "theme":"neutral",
      "themeVariables":{
        "labelBackgroundColor":"black",
        "clusterBkg":"#FFFFFF",
        "textColor":"grey"
      }
    }
  }%%
  %% https://books.google.nl/books?id=CBQ-EAAAQBAJ&pg=PA352&dq=labelBackgroundColor
  %%https://github.com/mermaid-js/mermaid/blob/develop/docs/theming.md

  graph LR
    subgraph Run once
      START1[Observed spectrum +<br />boundary conditions] ---> A[ReverseRADEX] ---> END1[Physical conditions]
    end

    subgraph Run many times
      START2[Physical conditions] ---> B[RADEX] ---> END2[Model spectrum]
    end


    %% https://stackoverflow.com/a/50270505
    style START1 fill:#FFFFFF, stroke:#FFFFFF
    style START2 fill:#FFFFFF, stroke:#FFFFFF
    style END1 fill:#FFFFFF, stroke:#FFFFFF
    style END2 fill:#FFFFFF, stroke:#FFFFFF
  ```

  **Figure 1:** Flow diagram showcasing the workflow of RADEX vs. ReverseRADEX.

</div>


<br />

To obtain optimal parameter estimates + uncertainties, ReverseRADEX employs an algorithm chain shown in Figure [2](#Figure2),


<div id="Figure2" align="center">

  ```mermaid
  %%{
    init:{
      "theme":"neutral",
      "themeVariables":{
        "labelBackgroundColor":"black",
        "textColor":"grey"
      }
    }
  }%%
  %% https://books.google.nl/books?id=CBQ-EAAAQBAJ&pg=PA352&dq=labelBackgroundColor
  %%https://github.com/mermaid-js/mermaid/blob/develop/docs/theming.md

  graph TD
    START[Line spectra + parameter bounds] .-> A2[Initial guess: <br /> brute force grid search]
    A2 -->|Initial parameter estimates| B2[Refine estimates: <br /> Levenberg-Marquardt <br /> Least Squares]
    B2 -->|Refined parameter estimates| C2[Uncertainty budget: <br /> MCMC]
    C2 .-> END[Parameter + uncertainty estimates]


    %% https://stackoverflow.com/a/50270505
    style START fill:#FFFFFF, stroke:#FFFFFF
    style END fill:#FFFFFF, stroke:#FFFFFF
  ```


  **Figure 2:** Flow diagram showcasing the optimizing algorithm chain used in ReverseRADEX.

</div>


<br />

See the following BSc thesis, [fse.studenttheses.ub.rug.nl/ReverseRADEX](http://fse.studenttheses.ub.rug.nl/id/eprint/25088), for further details on and discussing of (the development of) ReverseRADEX.

<br />



<!-- omit in toc -->
## Table of Contents

<!-- use  `` inside [] to create grey box, and use " " inside () to rename text shown on hover -->

- [Getting started](#getting-started)
  - [Dependencies](#dependencies)
  - [Installation](#installation)
- [Usage](#usage)
  - [Input](#input)
    - [terminal](#terminal)
    - [Jupyter notebook](#jupyter-notebook)
  - [output (files)](#output-files)
    - [Console](#console)
    - [csv](#csv)
    - [chains/walkers?](#chainswalkers)
    - [plots?](#plots)
- [3. Version History/changelog](#3-version-historychangelog)
- [License(s)](#licenses)
- [Acknowledgments](#acknowledgments)

<br />

<details closed>
  <summary>
    Code folder structure
  </summary>
  <br />

  <!-- FIXME: make it look nicer (in a code block it looks much nicer but you loose hyperlinks?, ...) ALSO add a descriptions see e.g. https://github.com/yangcht/radex_emcee#directory-structure
  -->
  [:package: ReverseRadex/](https://gitlab.astro.rug.nl/mooren/reverseradex) <br />
  &nbsp; ├── [:open_file_folder: fitting/](./fitting)  <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [find_initial_guess.py](./fitting/find_initial_guess.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [fitting_helper_functions.py](./fitting/fitting_helper_functions.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [LM.py](./fitting/LM.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [MCMC.py](./fitting/MCMC.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; └── [\_\_init__.py](./fitting/\__init__.py) <br />
  &nbsp; ├── [:open_file_folder: save_plot/](./save_plot)  <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [plot.py](./save_plot/plot.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [save.py](./save_plot/save.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [save_plot_helper.py](./save_plot/save_plot_helper.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; └── [\_\_init__.py](./save_plot/\__init__.py) <br />
  &nbsp; ├── [:open_file_folder: user_input/](./user_input)  <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [constant_input.py](./user_input/constant_input.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [input_functions.py](./user_input/input_functions.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [read_user_data.py](./user_input/read_user_data.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; ├── [variable_input.py](./user_input/variable_input.py) <br />
  &nbsp; │ &emsp;&nbsp;&nbsp; └── [\_\_init__.py](./user_input/\__init__.py) <br />
  &nbsp; ├── [main.ipynb](./main.ipynb) <br />
  &nbsp; └── [main.py](./main.py) <br />


</details>

<br />



## Getting started
<!-- linking to dependencies listed at the bottom feels wrong? maybe move up? -->

### Dependencies

ReverseRADEX has been developed (and tested) using python 3.6 but I expect it to work on later versions as well. The specific python modules required to run ReverseRADEX are listed in Table [1](#dependencies). But again, ReverseRADEX might work using different versions of the modules as well.

<br />

<div id="dependencies" align="center">

  | module          | version |  required  |
  | :-------------- | :-----: | :--------: |
  | [corner]        |  2.2.1  | [x] <br /> |
  | [emcee]         |  3.1.2  | [x] <br /> |
  | [matplotlib]    |  3.3.4  | [x] <br /> |
  | [numpy]         | 1.19.5  | [x] <br /> |
  | [pandas]        |  1.1.5  | [x] <br /> |
  | [scipy]         |  1.5.4  | [x] <br /> |
  | [spectralradex] |  1.1.3  | [x] <br /> |

  [corner]: https://www.pypi.org/project/corner/2.2.1
  [emcee]: https://www.pypi.org/project/emcee/3.1.2
  [matplotlib]: https://www.pypi.org/project/matplotlib/3.3.4
  [numpy]: https://www.pypi.org/project/numpy/1.19.5
  [pandas]: https://www.pypi.org/project/pandas/1.1.5
  [scipy]: https://www.pypi.org/project/scipy/1.5.4
  [spectralradex]: https://www.pypi.org/project/spectralradex/1.1.3

  **Table 1:** The main dependencies of ReverseRADEX, listed in [requirements.txt](./requirements.txt "requirements.txt").
</div>

The only tested operating system is (Ubuntu) Linux but ReverseRADEX should be able to run on other platforms (like MacOS, Windows) as well. \
I tried running SpectralRadex on Windows in the past but to no avail. The author(s) of Spectralradex do claim [OS independence](https://github.com/uclchem/SpectralRadex/blob/20768fdf577bd38b40f98cee0eb97400c48443a2/setup.py#L41) however.


### Installation

To install ReverseRADEX, it is **recommended** to create a virtual python (3.6) environment (e.g. using [venv](https://docs.python.org/3/library/venv.html)) and pip install the [requirements.txt](./requirements.txt "requirements.txt") file,

```shell
pip install requirements.txt
```


<br />
<div align="right">

  [![header](https://img.shields.io/badge/back_to-TOC-grey?style=flat-square)](#table-of-contents)
</div>

---



## Usage

<!-- with subsection(s) on how to run specific "configuration" if I can think
of some?
ALSO sub-sections for input and output? or have output be an entirely different section. +++ output folder is created, mention what name and where!-->

```shell
python main.py
```

<!-- highlight that molfile needs to be full path AND shorter than 80 character? (fortran limitation and just how i coded it?, see how spectralradex did it? that works fine right?) -->

<!-- example? main.py and main.ipynb way with gifs/figures? -->
<!-- figure out how to link to files in the reverseradex folder? -->
run main.py or main.ipynb if you prefer not to use a terminal. Pre-applied settings are present in main.ipynb (3rd cell). \
*datfile.dat* is the observed data file with a header (the first line starting with \#) indicating what units are used (1: T_R [K], 2: F [K km s$^{−1}$], 3: F [erg cm$^{−2}$ s$^{−1}$] (e.g. "# 1" means the units are intensities T_R). The first column contains the frequencies in GHz, the 2nd column indicates the line strengths in terms of the specified units in the header, and the last column contains the uncertainties (leave blank if no uncertainties). \
*molfile.dat* is the molecular data file containing collision and spectroscopic information, following the format of the Leiden Atomic and Molecular Database ([LAMDA](https://home.strw.leidenuniv.nl/~moldata/)).

The program runs on its own after than and in the case of main.py (terminal version), the input should be self explanatory beyond what is stated above.

A better README should follow soon.




### Input

#### terminal

asked line by line...

<details closed>
  <summary>
    Entering parameters (click me)
  </summary>
  <br />

  ```shell
  python main.py
  ```

  results in ...

  ```shell
  Enter molecular file path '*.dat': <full_path_to_molecular_data.dat>
  Enter data file path '*.dat': <full_path_to_spectra_data.dat>
  Enter background radiation field [K]: 2.73
  Enter line  width [km/s]: 1
  Enter a geometry (1=sphere, 2=LVG, 3=slab): 1
  Fit the kinetic temperature? (y/n): y
  Enter minimum kinetic gas temperature [K]: 5
  Enter maximum kinetic gas temperature [K]: 150
  Fit the column density? (y/n): y
  Enter minimum column density [cm^-2]: 1e17
  Enter maximum column density [cm^-2]: 1e21
  Enter (another) collision partner's name ['h2', 'h', 'e-', 'p-h2', 'o-h2', 'h+', 'he'] or enter 'no' if not: h2
  Fit h2's density? (y/n): y
  Enter minimum volume density [cm^-3] for all collision partners: 1e3
  Enter maximum volume density [cm^-3] for all collision partners: 1e7
  Enter (another) collision partner's name ['h', 'e-', 'p-h2', 'o-h2', 'h+', 'he'] or enter 'no' if not: n
  ```

</details>


this results in the following overview of the input parameters...


<details closed>
  <summary>
    parameter overview
  </summary>
  <br />

  ```shell
  Selected molfile path              : '<full_path_to_molecular_data.dat>'
  Selected datafile path             : '<full_path_to_spectra_data.dat>'
  Selected line strength units       : FLUX (erg/cm2/s)
  uncertainties included             : yes


  [name of parameter, parameter value, (lower bound, upper bound), fit parameter?]
  If a parameter is fit, "parameter value" is a dummy number and can be ignored.
  If not fit, the boundaries are dummy numbers.
  0.0 just indicates SpectralRadex to not use this collision partner.

  Selected minimum and maximum
  kinetic gas cloud temperature      : ['tkin', 72.5, (5.0, 150.0), True] K
  Selected background radiation field: 2.73 K
  Selected minimum and maximum
  column densities                   : ['cdmol', 4.9995e+20, (1e+17, 1e+21), True] cm^-2
  Selected volume densities [cm^-3],
  h2                                 : ['h2', 4999500.0, (1000.0, 10000000.0), True]
  h                                  : ['h', 0.0, (1000.0, 10000000.0), False]
  e-                                 : ['e-', 0.0, (1000.0, 10000000.0), False]
  p-h2                               : ['p-h2', 0.0, (1000.0, 10000000.0), False]
  o-h2                               : ['o-h2', 0.0, (1000.0, 10000000.0), False]
  h+                                 : ['h+', 0.0, (1000.0, 10000000.0), False]
  he                                 : ['he', 0.0, (1000.0, 10000000.0), False]
  Selected line width                : 1.0 km/s
  Selected minimum and maximum
  frequency                          : (230.30746200000002, 1268.2827687687688) GHz
  Selected geometry                  : uniform sphere

  Continue to the fitting process? (y/n)
  ```

</details>


which ends with the request of continuing to the fitting process if the input parameters are to your liking. This looks as follows ...


<details closed>
  <summary>
    fitting process
  </summary>
  <br />

  ```shell
  
  ```

</details>



<br />

#### Jupyter notebook

<!-- should be identical to main.py but just as a jupyter notebook? test this or mention the differences if there are any -->

same output as terminal pretty much but then in Jupyter notebook...

<details closed>
  <summary>
    main.ipynb (cell 2: input)
  </summary>
  <br />

  <!-- This is cell 2 in [main.ipynb](./main.ipynb) where user_molfile is the molecular data file from LAMDA and user_datfile are the observed line data. -->

  ```python
  user_molfile  = '<full_path_to_molecular_data.dat>'  # LAMDA database
  user_datfile  = '<full_path_to_spectra_data.dat>'  # observations
  freq_indices  = data_retrieval.get_molfile_frequency_index(user_datfile,
                                                            user_molfile)
  freq          = data_retrieval.get_frequencies(freq_indices, user_molfile)
  user_mol_frequencies, freq_min, freq_max, number_of_lines_total = freq
  freq_range    = (freq_min, freq_max)


  units             = data_retrieval.get_user_units(user_datfile)
  uncertainties     = data_retrieval.uncertainties_included(user_datfile)
  (y_observed,
  y_uncertainties) = data_retrieval.line_strengths(user_datfile,
                                                    uncertainties)

  # variable parameters.
  # [name parameter, inital guess, (bound_low, bound_upp), fit the parameter?]
  temp_kin = ['tkin', 131, (10.0, 750.0), True]  # 0.1 < tkin < 1e4 [K]
  coldens  = ['cdmol', 3e16, (1e10, 5e21), True]  # 1e5 < cdmol 1e25 [cm^-2]
  # 'collision partner':(init guess, fit parameter?)
  voldens  = {
      'h2':(3e4, True), 'h':(0.0, False), 'e-':(0.0, False),
      'p-h2':(0, False), 'o-h2':(0.0, False), 'h+':(0.0, False),
      'he':(0.0, False), 'min_max':(1e3, 1e7)
  }  # 1e-3 < collision partner < 1e13 [cm^-3]

  # constant parameters.
  Tbg  = 2.73  # K
  dv   = 1.0   # km s^-1
  geom = 1     #(1=sphere, 2=LVG, 3=slab)
  # just for displaying purposes,
  geom_name = 'uniform sphere'
  ```

</details>

<!-- link to the output thing in console part that will also happen here but just in jupyter cells? -->

<br />


#### Configuration file

<details closed>
  <summary>
    config.ini
  </summary>
  <br />

  ...

  <!-- the indentation is for readability, see [docs.python.org/configparser/indentation](https://docs.python.org/3/library/configparser.html#:~:text=multiline_values,value) for how python handles indentation as if its a single line such that types can be inferred using [docs.python.org/eval](https://docs.python.org/3/library/functions.html?highlight=eval#eval) as normal. -->

  ```ini
  ...
  ```

</details>

<!-- link to the output thing in console part that will also happen here but just in jupyter cells? -->

<br />


### output (files)

#### Console


#### csv


#### chains/walkers?
<!-- output to do your own statistics with AND/OR GTC corner plot? -->

#### plots?



<br />
<div align="right">

  [![header](https://img.shields.io/badge/back_to-TOC-grey?style=flat-square)](#table-of-contents)
</div>

---



<!-- ## FAQ <!-- rename to something that includes warnings or issues or something? e.g "known issues"? but that is only issues? so little more general? (one "issue" would be that brute force grid search could get stuck in local minima easily unless computation time is heavily increased, defeating the point of having a "quick" way to obtain some results) -->

<!-- ADD THAT THE INITIAL BRUTE FORCE GRID SEARCH SOMETIMES GETS STUCK IN LOCAL MINIMA AND THUS THE LM AND MCMC ALGORITHMS ARE OPTIMIZING IN A LOCAL MINIMA (see BSc thesis sec 7.? for further details?) [MAYBE hIhLgiHT ThIS at The TOp As WEll] -->

<!-- See sec 4.2 of BSc thesis + van der Tak 2007 about RADEX assumptions/limitations. AND see sec 7 (discussion?, maybe sec 5-reverseradex with limitations/assumptions section?) About assumptions/limitations with regards to Reverseradex. -->


<br />

<br />
<div align="right">

  [![header](https://img.shields.io/badge/back_to-TOC-grey?style=flat-square)](#table-of-contents)
</div>

---



## 3. Version History/changelog
<!-- have hyperlinks to the commits of each version name (use this so for future renditions of the project the changelog can be automated more easily? USE and REFERENCE https://semver.org/ ? -->
<!-- Have a separate branch named "utilities" where there is a detailed changelog once this gets too much? AND that is also where the images used in this README.md are hosted? AND where you can find the licenses of all other software used like spectralradex and RADEX? BUT do refer to these in README.md, just store them in separate branch -->


[`Version 0.1.2`](https://gitlab.astro.rug.nl/mooren/reverseradex/-/tree/4a8fee6383ca2b950c8b322d96f3917077f8b621)
<!-- include version number somewhere in package from this point onwards? -->

- **Updated** README to include proper instructions.
- **Fixed** output folder not being created due to missing parent folder.

<br />


[`Version 0.1.1`](https://gitlab.astro.rug.nl/mooren/reverseradex/-/tree/03fc6c7b3577dc487e473dfefc20a8ed6b108081)
<!-- the fix in main.py and main.ipynb or whatever? + Typos in README.md + added license + ??? -->

- 

<br />


[`Version 0.1`](https://gitlab.astro.rug.nl/mooren/reverseradex/-/tree/03fc6c7b3577dc487e473dfefc20a8ed6b108081)

- Initial ***Release***


<br />
<div align="right">

  [![header](https://img.shields.io/badge/back_to-TOC-grey?style=flat-square)](#table-of-contents)
</div>

---



<!-- ## Work in Progress/Roadmap? (if I decide to work some more on the project and what the future goals are?)
!!! todo
    - make plotting (matpltolib, corner) optional dependencies.
    - ???
<br />

<br />
<div align="right">

  [![header](https://img.shields.io/badge/back_to-TOC-grey?style=flat-square)](#table-of-contents)
</div>

---
-->



<!-- ## Related/Alternative/Similar Software
like https://github.com/yangcht/radex_emcee ?, https://github.com/jrka/pyradexnest ?, https://github.com/richteague/radexcee ?, https://github.com/Marcus-Keil/UCLCHEMCMC ?, https://github.com/avantyghem/pyradex_mcmc ?, ...
Also a brief description on how it is different?

<br />

<br />
<div align="right">

  [![header](https://img.shields.io/badge/back_to-TOC-grey?style=flat-square)](#table-of-contents)
</div>

---
-->

## License(s)

<div align="center">

  | License *file* | License type |
  | :---: | :---: |
  | [RADEX](./LICENSE-RADEX) | Source code comment regarding referencing |
  | [ReverseRADEX](./LICENSE) | MIT |

</div>

<br />
<div align="right">

  [![header](https://img.shields.io/badge/back_to-TOC-grey?style=flat-square)](#table-of-contents)
</div>

---



## Acknowledgments
<!-- something for a readme template?, idk -->

This program was developed under the supervision of Prof. Dr. Floris F.S van der Tak.

<br />

<div align="center">

  Further Acknowledgments:

  | source | description |
  | :-----: | :--------: |
  | [shields.io](https://shields.io/) | (embedding links in) icons |
  | [choosealicense.com](https://choosealicense.com/) | license template |
  | [github.com/gitlab-emoji](https://github.com/yodamad/gitlab-emoji) | emoji list for GitLab|
  | [mermaid.github.io](https://mermaid-js.github.io/) | generating diagrams|

</div>

<br />
<div align="right">

  [![header](https://img.shields.io/badge/back_to-TOC-grey?style=flat-square)](#table-of-contents)
</div>
