#!/usr/bin/env python3

# module imports
from numpy import loadtxt, ones

# relative imports
from user_input.input_functions import in_between_check


class DataRetrieval:
    # FIXME: things that are used multiple times should go into __init__?
    #def __init__(self):
    #    return


    # FIXME: just use numpy.loadtxt, array.T for transposing and .astype(float)
    # to transform the elements of the array from str to float instead of
    # "transpose_float_convert_list"? runtime is really not an issue here.

    
    ### general functions ###
    def get_file_lines(self, data_file_location):
        """get the file lines of user supplied data file in a list.

        Args:
            data_file_location (str): file location on system of data file.
            

        Returns:
            list: list of file lines of the user supplied data file.
        """
        
        with open(data_file_location, 'r') as data_file:
            # TODO: add a check to see if file is empty, 
            # perhaps if possible also if there are enough data points
            # for the number of parameters chosen to fit for LM to still
            # work --> N + 1 data points required (N is number of fit
            # parameters)
            data_file_lines = data_file.readlines()
        return data_file_lines


    def transpose_float_convert_list(self, input_list, selected_row):
        """transpose N x M list and convert elements type of a single 
        row to float.

        Args:
            input_list (list): list to be transposed and converted.
            selected_row (int): the index of the row that should be returned
            

        Returns:
            list: transposed list with float elements.
        """
        
        # FIXME: try and use zip(*list)?
        transposed_list = list(map(lambda *untransposed: list(untransposed),
                                   *input_list))

        transposed_list = transposed_list[selected_row]
        
        # FIXME: take this out when I also include lineID and just do it
        # where it is needed outside of this function.
        transposed_float_list = list(map(float, transposed_list))
        
        return transposed_float_list
    ### general functions ###


    ### data retrieving functions ###
    def get_user_units(self, data_file_location):
        """retrieves the line strength units from the user supplied data file.

        Args:
            data_file_location (str): file location on system of data file.

        Raises:
            ValueError: checks if unit selection is read by python
            properly.
            

        Returns:
            int: integer describing which line strength units are to be used.
        """
        
        units_line = self.get_file_lines(data_file_location)[0]
        # FIXME?: perhaps use units_line.find(1,2,3) or something?
        # or maybe a for loop and check
        # "for units in [1,2,3]: for line in lines: if units in line: break?
        units_retrieved = int(units_line.strip()[-1])

        valid_units = ['T_R (K) => # 1',
                       'FLUX (K*km/s) => # 2',
                       'FLUX (erg/cm2/s) => # 3']
        valid_units_int  = [1,2,3]
        valid_units_name = ['T_R (K)', 'FLUX (K*km/s)', 'FLUX (erg/cm2/s)']
        if units_retrieved not in valid_units_int:
            raise ValueError("Units selected in the header of " +
                             f'"{data_file_location}" are invalid. ' +
                             "Please enter one of the following units, " +
                             f"{valid_units}, in the header by typing " +
                             '"# int".')
        
        return valid_units_name[units_retrieved - 1]


    def get_molfile_frequencies(self, molecular_file):
        """get all the frequencies as floats in a list from the
        selected molfile.

        Args:
            molecular_file (str): file location on system of molecular file.
            

        Returns:
            list: list of frequencies with float type.
        """
        
        contents_molfile = self.get_file_lines(molecular_file)
        # FIXME: this only works if all molfiles are structured the same way
        # and some inconsistencies in LAMDA files definitley ocurred.
        trans = ('!TRANS', '! TRANS')
        numbr = ('!NUMBER', '! NUMBER')
        index_lower = None
        index_upper = None
        for molfile_line in contents_molfile:
            if molfile_line.startswith(trans):
                index_lower = contents_molfile.index(molfile_line)
            
            if molfile_line.startswith(numbr):
                index_upper = contents_molfile.index(molfile_line)
            
            # since we are after the first occurrence of '!TRANS' and
            # subsequent '!NUMBER' in the molfile, this if statement
            # should suffice in finding the indices
            if ((index_lower and index_upper) != None
                and index_upper > index_lower):
                break
        
        radiative_transitions = contents_molfile[index_lower + 1:index_upper]
        radiative_transitions_split = [split_line.split()
                                       for split_line
                                       in radiative_transitions]
        
        # "transposing" the list to select the column (now row) of frequencies.
        # index 4 indicates the frequency column (now row) in the molfile.
        molfile_frequencies = self.transpose_float_convert_list(
            radiative_transitions_split, 4)
        
        return molfile_frequencies


    # TODO/FIXME: if LAMDA file does not contain frequencies, this will not work
    # (spectralRadex itself will also not work) change the LAMDA file to
    # include frequencies in the correct column (get it from energy levels)?
    def get_molfile_frequency_index(self, data_file_location, molecular_file):
        """get the index of molecular file frequencies that match user
        supplied data file frequencies. The indices are to be used for
        cutting radex output to match user input later on (this is important)
        for MAGIX to work properly).

        Args:
            data_file_location (str): file location on system of user data.
            molecular_file (str): file location on system of molecular file.

        Raises:
            EOFError: checks if a specific line in user supplied data file
                    does not match any line in the selected molecular file.
                    

        Returns:
            list: indices of molfile that match user supplied data.
        """
        
        data_lines = self.get_file_lines(data_file_location)[1:]
        
        data_lines_split = [data_line.split()
                            for data_line
                            in data_lines]
        
        # index 0 selects first row (frequencies) in user supplied data file.
        user_freqs = self.transpose_float_convert_list(data_lines_split, 0)

        # gets the frequencies (float) of the selected molfile in a list.
        molfile_frequencies = self.get_molfile_frequencies(molecular_file)

        # bw ("bandwith") to within which a user supplied frequency should 
        # match the molfile frequency.
        # TODO: dynamically change "bw" based on molfile by seeing what is 
        # the closest frequency discrepancy and take half that?
        # For now just with 0.001, 0.01 or 0.1 or something as max "bw"?
        bw = 0.001
        matching_index   = []
        for user_freq in user_freqs:
            for iter_index, molfile_freq in enumerate(molfile_frequencies):
                if (user_freq * (1-bw) <= molfile_freq <= user_freq / (1-bw)):

                    matching_index += [iter_index]
                    break

            # FIXME: make it so it returns all the lines that do not match.
            # ALSO be clearer about how a line is matched (using bw)?
            # FIXME: find a better error to return, instead of EOFError?
            else:
                raise EOFError(f"The line corresponding to {user_freq}" +
                               f" GHz in '{data_file_location}'" +
                               " does not match any frequency in the " +
                               f"selected molfile: '{molecular_file}'.")
        
        return matching_index


    def get_frequencies(self, frequency_indices, molecular_file):
        """get the minimum and maximum frequency [GHz] from the molfile and
        user supplied data. it is ensured that the minimum and maximum
        frequency are included in the frequency range by means of a
        "bw" (bandwidth).

        Args:
            frequency_indices (list): indices of matching frequencies.
            molecular_file (str): file location on system of molecular file.
            

        Returns:
            tuple: minimum and maximum frequency
        """
        
        all_frequencies = self.get_molfile_frequencies(molecular_file)
        number_of_freqs = len(all_frequencies)
        
        frequencies_that_match = [all_frequencies[index_match]
                                  for index_match
                                  in frequency_indices]
        
        # ensuring that all frequencies are within the minimum and maximum.
        # NOTE: this might prove problematic when frequencies in LAMDA
        # file are unordered and certain output will be cut by SpectralRadex
        # and thus not matched to user data. (see line ~217 of main.py)
        # works fine for ordered frequency files.
        bw = 0.001
        freq_min = min(frequencies_that_match) * (1 - bw)
        freq_max = max(frequencies_that_match) / (1 - bw)

        # check if frequencies are within RADEX limits.
        in_between_check(0, 3e7, freq_min, 'minimum frequency read from ' +
                         'molecular file (expects GHz)')

        in_between_check(0, 3e7, freq_max, 'maximum frequency read from ' +
                         'molecular file (expects GHz)')

        return frequencies_that_match, freq_min, freq_max, number_of_freqs


    def uncertainties_included(self, data_file_location):
        """determine if there are uncertainties included in the user
        supplied data file by checking the amount of columns.

        Args:
            data_file_location (str): file location on system of data file.

        Raises:
            Exception: if the number of columns is invalid. The excpected
            number is 2 (frequencies and line strengths) or 3 (frequencies,
            line strengths and line strength uncertainties).
            

        Returns:
            str: either 'yes' or 'no' to be used as input for MAGIX to tell
            it that uncertainties are included or not.
        """
        
        # TODO: add support for if there are some lines with, and some
        # lines without uncertainties (for those without, just set it
        # equal to one, as they are only used in a chi2 calculation?)     
           
        # [1:] to exclude header.
        data_lines = self.get_file_lines(data_file_location)[1:]
        
        number_of_columns = len(data_lines[0].split())
        if number_of_columns == 3:
            return 'yes'
        elif number_of_columns == 2:
            return 'no'
        else:
            raise Exception(f"The number of columns = {number_of_columns}" +
                            f" in {data_file_location} is invalid. " +
                            "The excpected number is 2 (frequencies and " +
                            "line strengths) or 3 (frequencies, line " +
                            "strengths and line strength uncertainties).")
            
        return


    def line_strengths(self, user_data_file, uncertainty):
        """extract the line strength column (with uncertainties) from the
        user supplied data file. These uncertainties are only used for
        calculating the chi^2 values so the default uncertainties = 1 (or
        any other constant) since they have no effect then.

        Args:
            user_data_file (str): user supplied data file directory.
            
            uncertainty (str): uncertainties included ('yes' -OR- 'no')
            

        Returns:
            tuple: 1 numpy array with line strenghts and 1 numpy array
            with line strength uncertainties.
        """
        
        data = loadtxt(user_data_file).T
        if uncertainty == 'no':
            line_strenghts = data[1]
            return (line_strenghts, ones(line_strenghts.shape[0]))
        else:
            line_strenghts, line_strenght_uncertanties = data[1:]
            return (line_strenghts, line_strenght_uncertanties)

        return


    
    ### data retreiving functions ###

