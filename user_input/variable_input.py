#!/usr/bin/env python3
#%%
# relative imports
from user_input.input_functions import (
    numeric_input,
    min_max_check,
    in_between_check,
    yay_or_nay,
    re_enter_wrapper,
    collision_check
)


class VariableParamters:
    #def __init__(self):
    #    return    

    
    @re_enter_wrapper
    def kinetic_temperature_input(self):
        """function to set kinetic temperature boundaries based on
        user input, or return default values.
        

        Returns:
            float, tuple, bool: parameter value, (minimum and maximum
            kinetic temperature), fit parameter.
        """

        temp_kin_name = 'tkin'
        
        temp_kin_fit = (yay_or_nay("Fit the kinetic temperature? (y/n): ")
                        or False)

        if temp_kin_fit == False:
            temp_kin = (
                numeric_input("Enter kinetic gas temperature [K]: ")
            )
            if temp_kin == '':
                print("No kinetic temperature is entered. Enter " +
                      "a kinetic temperature in Kelvin.")
                return 'dummy'
            
            # check if 'temp_kin' is within RADEX boundary limits.
            btw_check = (
                in_between_check(0.1, 1e4, temp_kin, temp_kin_name) == None
            )
            if not btw_check:
                return 'dummy'
            
            return [temp_kin_name, temp_kin, (0.1, 1e4), temp_kin_fit]
        
        
        temp_kin_min = (numeric_input(
            "Enter minimum kinetic gas temperature [K]: ")
                or 10.0)
        # check if 'temp_kin_min' within bounds that RADEX operates.
        btw_check = (
            in_between_check(0.1, 1e4, temp_kin_min,
                         'minimum kinetic temperature') == None
        )
        if not btw_check:
            return 'dummy'
        
        temp_kin_max = (numeric_input(
            "Enter maximum kinetic gas temperature [K]: ")
                or 500.0)
        # check if 'temp_kin_max' within bounds that RADEX operates.
        btw_check = (
            in_between_check(0.1, 1e4, temp_kin_max,
                         'maximum kinetic temperature') == None
        )
        if not btw_check:
            return 'dummy'

        # checks if maximum > minimum.
        mm_check = (
            min_max_check(temp_kin_min, temp_kin_max, temp_kin_name) == None
        )
        if not mm_check:
            return 'dummy'

        # will not be used by program and serves a dummy purpose to keep
        # the return in the expected shape.
        temp_kin = (temp_kin_max - temp_kin_min)/2
                  
        return [temp_kin_name, temp_kin, (temp_kin_min, temp_kin_max),
                temp_kin_fit]

    
    @re_enter_wrapper
    def column_density_input(self):
        """function to set column density boundaries based on
        user input, or return default values.
        

        Returns:
            float, tuple, bool: parameter value, (minimum and maximum
            column density), fit parameter.
        """

        cd_name = 'cdmol'
        
        cd_fit = (yay_or_nay("Fit the column density? (y/n): ") or False)

        if cd_fit == False:
            cd = (
                numeric_input("Enter column density [cm^-2]: ")
            )
            if cd == '':
                print("No column density is entered. Enter " +
                      "a column density in cm^-2.")
                return 'dummy'
            
            # check if 'tcd' is within RADEX boundary limits.
            btw_check = (
                in_between_check(1e5, 1e25, cd, cd_name) == None
            )
            if not btw_check:
                return 'dummy'

            return [cd_name, cd, (1e5, 1e25), cd_fit]
        
        
        cd_min = (numeric_input(
            "Enter minimum column density [cm^-2]: ")
                or 1e11)
        # check if 'cd_min' within bounds that RADEX operates.
        btw_check = (
            in_between_check(1e5, 1e25, cd_min,
                             'minimum column density') == None
        )
        if not btw_check:
            return 'dummy'
        
        cd_max = (numeric_input(
            "Enter maximum column density [cm^-2]: ")
                or 1e16)
        # check if 'cd_max' within bounds that RADEX operates.
        btw_check = (
            in_between_check(1e5, 1e25, cd_max,
                             'maximum column density') == None
        )
        if not btw_check:
            return 'dummy'

        # checks if maximum > minimum.
        mm_check = (
            min_max_check(cd_min, cd_max, cd_name) == None
        )
        if not mm_check:
            return 'dummy'
        
        cd = (cd_max - cd_min)/2
                       
        return [cd_name, cd, (cd_min, cd_max), cd_fit]
    

    @re_enter_wrapper
    def collision_densities_input(self):
        """function to set volume densities (and boundaries) based on
        user input, or return default values.
        

        Returns:
            dict[tuple]: dictionary with collision partner volume
            densities (float) and matching "fit parameter?" indicator
            (bool).
        """

        # collision partners,
        h2    = (0.0, False)
        h     = (0.0, False)
        e     = (0.0, False)
        ph2   = (0.0, False)
        oh2   = (0.0, False)
        hplus = (0.0, False)
        he    = (0.0, False)
        
        nmin  = 1e-3
        n_min = nmin
        nmax  = 1e13
        n_max = nmax
        
        densities = {'h2':h2, 'h':h, 'e-':e, 'p-h2':ph2, 'o-h2':oh2,
                     'h+':hplus, 'he':he, 'min_max':(n_min, n_max)}

        vol_dens_names = ['h2', 'h', 'e-', 'p-h2', 'o-h2', 'h+', 'he']
        no = ['n', 'no', 'nah', 'nay', 'nope']
        # input loop that gets recalled on invalid input (@re_enter_wrapper).
        while True:
            if vol_dens_names == []:
                break
            
            collision_key = collision_check(
                "Enter (another) collision partner's name " +
                f"{vol_dens_names} or enter 'no' if not: ",
                vol_dens_names, no
            )
            if collision_key in no:
                break
            else:            
                collision_fit = yay_or_nay(
                    f"Fit {collision_key}'s density? (y/n): "
                )
                if collision_fit == True:
                    # checks if bounds have already been entered.
                    if (n_min is nmin and n_max is nmax):
                        # TODO: have individual limits for all
                        # collision partners.
                        n_min = (numeric_input(
                            "Enter minimum volume density" +
                            " [cm^-3] for all collision " +
                            "partners: "
                            ) or n_min
                        )
                        nmin = n_min
                        # check if 'n_min' within bounds that RADEX operates.
                        btw_check = (
                            in_between_check(
                                1e-3, 1e13, n_min, 'minimum volume density'
                            ) == None
                        )
                        if not btw_check:
                            return 'dummy'
                        
                        n_max = (numeric_input(
                            "Enter maximum volume density" +
                            " [cm^-3] for all collision " +
                            "partners: "
                            ) or n_max
                        )
                        # check if 'n_max' within bounds that RADEX operates.
                        btw_check = (
                            in_between_check(
                                1e-3, 1e13, n_max, 'maximum volume density'
                            ) == None
                        )
                        if not btw_check:
                            return 'dummy'
                        
                        # checks if maximum > minimum.
                        mm_check = (
                            min_max_check(n_min, n_max,
                                          'volume density') == None
                        )
                        if not mm_check:
                            return 'dummy'
                        
                        densities['min_max'] = (n_min, n_max)
                        collision_value = (n_max - n_min)/2
                else:
                    collision_value = numeric_input(
                        f"Enter density of {collision_key}: "
                    )
                    if collision_value == '':
                        print("Collision partner density is not set. " +
                              f"User entered '{collision_value}'.")
                        return 'dummy'
                    # check if 'collision_value' within RADEX bounds.
                    btw_check = (
                        in_between_check(
                            1e-3, 1e13, collision_value, f'{collision_key}'
                        ) == None
                    )
                    if not btw_check:
                        return 'dummy'


                collision_value_dummy = (n_max - n_min)/2
                if collision_value != collision_value_dummy:
                    pass
                else:
                    collision_value = collision_value_dummy
                
                densities[collision_key] = (collision_value, collision_fit)

                vol_dens_names.remove(collision_key)

        # check if a density or bounds are entered for any
        # collision partner.
        densities_copy = densities.copy()
        del densities_copy['min_max']
        density_values = [collision_partner[0]
                          for collision_partner
                          in densities_copy.values()]
        # check if any entry in density_values is a float != 0.0
        # since python reads bool(0.0) = False and nonzero floats
        # as True.
        if any(density_values) != True:
            print("No volume density is set.")
            return 'dummy'            

        # check if parameters are within boundary limits.
        vol_invalid = []
        for key, value in densities.items():
            conditions = [
                value[1] == True,
                value[0] != 0.0,
                value != densities['min_max'],
                not (n_min < value[0] < n_max)
            ]
            if all(conditions):
                vol_invalid += [(n_min, n_max, value[0], key)]

        if vol_invalid != []:
            for col_partner in vol_invalid:
                n_min, n_max, value, key = col_partner
                print(f"{key} = {value} is not within limits [{n_min};" +
                      f" {n_max}].")
            return 'dummy'
        
        return densities
    

# %%