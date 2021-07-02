#!/usr/bin/env python3
#%%
from user_input.input_functions import (
    numeric_input,
    in_between_check,
    re_enter_wrapper
)


class ConstantParamaters:
    #def __init__(self):
    #    return
    
    
    def molfile_input(self):
        """function to ask for molecular file path.

        Raises:
            FileNotFoundError: User did not supply a molecular file.
            

        Returns:
            str: string of name refering to the molecular file used.
        """
        
        user_molfile = input(
            "Enter molecular file path '*.dat': ").replace(' ', '')
        if user_molfile == '':
            raise FileNotFoundError("User did not supply a " +
                                    "molecular file")
        
        extension = '.dat'
        if not user_molfile.endswith(extension):
            user_molfile += extension
        
        return user_molfile


    def datafile_input(self):
        """function to ask for data file path.

        Raises:
            FileNotFoundError: User did not supply a data file.
            

        Returns:
            str: string of name refering to the molecular file used.
        """

        user_datafile = input(
            "Enter data file path '*.dat': ").replace(' ', '')
        if user_datafile == '':
            raise FileNotFoundError("User did not supply a " +
                                    "data file path")

        extension = '.dat'
        if not user_datafile.endswith(extension):
            user_datafile += extension
        
        return user_datafile
    
    
    @re_enter_wrapper
    def background_radiation_input(self):
        """function to set background radiation field based on user input,
        or return a default value.
        

        Returns:
            float: either user input or standard parameter.
        """
        # TODO/FIXME: how is the option of a user supplied radiation field
        # handeled by (spectral) radex, since that is what needs to be
        # the input then instead of background temperature?

        temp_background = (numeric_input(
            "Enter background radiation field [K]: ") or 2.73)

        # check if 'temp_background' within bounds that RADEX operates.
        btw_check = (
            in_between_check(-1e4, 1e4, temp_background,
                             'background radiation field') == None
        )
        if not btw_check:
            return 'dummy'
        
        return temp_background
    
    
    @re_enter_wrapper
    def line_width_input(self):
        """function to set line width [km/s] based on user input,
        or return a default value.
        

        Returns:
            float: either user input or standard parameter.
        """

        line_width = (numeric_input("Enter line  width [km/s]: ") or 1.0)
        
        # check if 'line_width' within bounds that RADEX operates.
        btw_check = (
            in_between_check(1e-3, 1e3, line_width, 'line width') == None
        )
        if not btw_check:
            return 'dummy'
        
        return line_width

    
    @re_enter_wrapper
    def geometry_input(self):
        """function set geometry based on user input, or return uniform
        sphere as default geometry.

        Raises:
            ValueError: not a valid geometry.
            

        Returns:
            int: integer referring to geometry.
        """
        sphere = ['1', 'sphere', 'uni']
        lvg    = ['2', 'lvg']
        slab   = ['3', 'slab']
        cloud_geometry = input(
            "Enter a geometry (1=sphere, 2=LVG, 3=slab): "
        ).replace(' ', '').lower()
        
        # FIXME: take out default geometry and always ask user?
        if cloud_geometry == '':
            return int(1), 'uniform sphere'
        elif cloud_geometry in sphere:
            return 1, 'uniform sphere'
        elif cloud_geometry in lvg:
            return 2, 'LVG'
        elif cloud_geometry in slab:
            return 3, 'slab'
        else:
            print("Not a valid geometry. Choose one " +
                  "of three geometries;\nuniform sphere: "+
                  f"               {sphere}\n" +
                  "large velocity gradient " +
                  f"(LVG): {lvg}\nplane-parallel " +
                  f"slab:           {slab}")
            return 'dummy'
        
        return


# %%

