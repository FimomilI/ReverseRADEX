#!/usr/bin/env python3


def re_enter_wrapper(fnc):
    """a wrapper that recalls the function if input is invalid or
    unsatisfactory.

    Args:
        fnc (function): the function to be wrapped and checked for
        validity of input and recalled if necessary.


    Returns:
        funcion: the wrapper function
    """
    
    def re_enter_or_return(*args, **kwargs):
        """function that creates a while loop of function calls to
        the function to be wrapped, until the returned value is
        satisfactory.
        

        Returns:
            function: recalls the function.
        """
        
        while True:
            function_return = fnc(*args, **kwargs)
            if function_return == 'dummy':
                continue
            else:
                return function_return
            
        return 

    return re_enter_or_return


@re_enter_wrapper
def numeric_input(query):
    """function that is called to either return user input or standard
    parameter if input is omitted. If user input is called,
    the input is checked to be either int or float.

    Args:
        query (str): prompt for user input.

    Raises:
        TypeError: Input is not an integer or float.
        

    Returns:
        str, float: empty string (read by python as None) prompt or
        user input as a float.
    """
    
    entry = input(query)
    if entry == '':
        return entry

    try:
        # to allow for scientific/exponential notation.
        if float(entry):
            return float(entry)
    except ValueError:
        pass

    # if input is not '' (empty) or in scientific notation, check if 
    # input is numeric (float/int)
    entry_check = entry.replace(' ', '').strip()
    if_conditions =(
        entry_check.isdigit() or
        (entry_check.replace('.', '', 1).isdigit() and
         entry_check.count('.') < 2)
    )
    if not if_conditions:
        print("Input is not an integer or float, or is " +
              f"negative. User input was '{entry}'")
        return 'dummy'

    # TODO/FIXME: what should be the case for entry == 0? Currently it 
    # seems to ignore the entry (read by python as "False"?)
    # especially important for Tbg and adding a tabulated radiation
    # background.
    # if int(entry) == 0 and float(entry) == 0.0:
    #     raise ValueError(f"Input must be positive. User input was {entry}")
    
    return float(entry)


def min_max_check(parameter_min, parameter_max, parameter_name):
    """checks if minimum of parameter is less than maximum
    of parameter.

    Args:
        prms_min (float): lower bound of parameter.
        
        prms_max (float): upper bound of parameter.
        
        parameter_name (str): name of parameter to check.
        

    Raises:
        ValueError: minimum is greater than maximum.
    """
    
    if parameter_min > parameter_max:
        print(f"The minimum {parameter_name} selected" +
              f" '{parameter_min}' is greater than" +
              f" the maximum '{parameter_max}'.")
        return 'dummy'
    
    return


def in_between_check(parameter_min, parameter_max,
                     parameter_value, parameter_name):
    """check if the parameter value is within the parameter limits.

    Args:
        prms_min (float): lower bound of parameter.
        
        prms_max (float): upper bound of parameter.
        
        parameter_value (float): value of parameter to be checked.
        
        parameter_name (str): name of parameter to check.
        

    Raises:
        ValueError: parameter value is not within the boundary limits.
    """
    
    # FIXME: make it clear when it talks about user defined limits and when
    # it discusses radex limits? radex limits are exclusive!
    if not (parameter_min < parameter_value < parameter_max):
        print(f"{parameter_name} = {parameter_value}, " +
              "is not within the limits of " +
              f"[{parameter_min}; {parameter_max}].")
        return 'dummy'
    
    return


@re_enter_wrapper
def yay_or_nay(query):
    """check if user wants to fit (a specific) parameter(s).

    Args:
        query (str): prompt for user input.

    Raises:
        ValueError: raises error if the fit is not declared properly.
        

    Returns:
        bool: True (fit parameter) False (do not fit parameter).
    """
    
    entry = input(query)
    
    if entry == '':
        return entry

    entry = entry.replace(' ', '')
    
    yes = ['y', 'yay', 'yes']
    no  = ['n', 'nay', 'no']
    while True:
        if entry in yes:
            return True
        elif entry in no:
            return False
        else:
            print(
                f"\n'{entry}' is not a valid input. Try entering " +
                f"one of either {yes} if you want to fit the " +
                f"parameter(s) or {no} if you do not want to fit " +
                "the parameter(s).\nThe default is 'no'"
            )
            return 'dummy'
    
    return


@re_enter_wrapper
def collision_check(query, collision_partner_names, no):
    """check if user entered a valid collision partner name. This only
    checks all the names that RADEX supports, not necessarily the names
    of collision partners actually present in the molecular data file.

    Args:
        query (str): query to raise user and request input.
        

    Returns:
        str: name of collision partner.
    """

    # collision_partner_names = ['h2', 'h', 'e-', 'p-h2', 'o-h2', 'h+', 'he']
    collision_partner_name = input(query).replace(' ', '').lower()
    conditions = (
        collision_partner_name not in collision_partner_names
        and collision_partner_name not in no
    )
    if conditions:
        print(
            f"\n'{collision_partner_name}' is not in " +
            f"'{collision_partner_names}'."
        )
        return 'dummy'
    else:
        return collision_partner_name
    
    return