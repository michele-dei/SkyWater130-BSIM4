#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 09:17:18 2025

@author: Michele Dei

*******************************************************************************
* Copyright 2025 Michele Dei 
* michele.dei@unipi.it
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************

Script: RMSE Computation from CSV Files

Purpose:
--------
This script reads multiple CSV files, extracts numerical data from the second 
column, and computes the Root Mean Square Error (RMSE) relative to either the 
first or last file in the list. It supports both linear and logarithmic RMSE 
calculations.

Functionality:
--------------
1. **Reads CSV Filenames from a Text File:**  
   - Reads a list of CSV filenames stored in a `.txt` file.  
   - If the file does not exist or is empty, the script terminates.

2. **Validates and Fixes CSV Extensions:**  
   - Ensures that each file has a `.csv` extension.  
   - If missing, appends `.csv` and prints a warning.

3. **Loads Data from CSV Files:**  
   - Reads the second column of each CSV file into a NumPy array.  
   - Skips files that do not have at least two columns.  

4. **Computes RMSE Between CSV Data:**  
   - Computes RMSE between each CSV file and a reference file.  
   - The reference file can be the **first** or **last** in the list.  
   - Supports both **linear** and **logarithmic (base-10)** RMSE calculations.  

5. **Command-Line Arguments:**  
   - `-first` : Uses the first CSV file as the reference (default: last).  
   - `-last`  : Uses the last CSV file as the reference.  
   - `-lin`   : Computes RMSE in a **linear** scale (default: logarithmic).  
   - `-log`   : Computes RMSE in a **logarithmic** scale.  

Usage:
------
Run the script from the terminal:
    $ python script.py <csv_list.txt> [-first | -last] [-lin | -log]

Where:
- `<csv_list.txt>` is a text file containing the paths to CSV files.
- The default behavior compares all CSVs to the **last** CSV file.
- The default RMSE calculation is **logarithmic** (`log10`).

Error Handling:
---------------
- **Missing Files:** The script prints an error if any input file is missing.
- **Insufficient Data:** If a CSV lacks a second column, it is skipped.
- **NaN or Non-Positive Values:** Logarithmic RMSE is not computed for non-positive values.
- **Empty Arrays:** If any extracted data array is empty, computation is skipped.

"""

import numpy as np
import pandas as pd
import argparse
import os

def rmse(arr1, arr2):
    """
    Calculates the Root Mean Square Error (RMSE) between two arrays.

    Args:
        arr1: The first array (e.g., predicted values).
        arr2: The second array (e.g., actual values).

    Returns:
        The RMSE value (float). Returns np.inf if arrays have different sizes.
        Returns np.nan if one of the arrays contains a nan value.
        Returns 0 if the arrays are empty.

    Raises:
        TypeError: If either input is not a numpy array.
    """

    if not isinstance(arr1, np.ndarray) or not isinstance(arr2, np.ndarray):
        raise TypeError("Inputs must be numpy arrays.")

    if arr1.size != arr2.size:
        return np.inf  # Or raise an exception if you prefer

    if arr1.size == 0:
        return 0

    if np.isnan(arr1).any() or np.isnan(arr2).any():
        return np.nan

    squared_errors = (arr1 - arr2)**2
    mean_squared_error = np.mean(squared_errors)
    root_mean_squared_error = np.sqrt(mean_squared_error)
    return root_mean_squared_error

def rmse_log10(arr1, arr2):
    """
    Calculates the RMSE between the base-10 logarithms of two arrays.

    Args:
        arr1: The first array.
        arr2: The second array.

    Returns:
        The RMSE of the log10 of the arrays (float). Returns np.inf if arrays have different sizes.
        Returns np.nan if one of the arrays contains a nan value or a non-positive value.
        Returns 0 if the arrays are empty.

    Raises:
        TypeError: If either input is not a numpy array.
    """

    if not isinstance(arr1, np.ndarray) or not isinstance(arr2, np.ndarray):
        raise TypeError("Inputs must be numpy arrays.")

    if arr1.size != arr2.size:
        return np.inf

    if arr1.size == 0:
        return 0

    if np.isnan(arr1).any() or np.isnan(arr2).any() or (arr1 <= 0).any() or (arr2 <= 0).any():
        return np.nan

    log_arr1 = np.log10(arr1)
    log_arr2 = np.log10(arr2)
    return rmse(log_arr1, log_arr2)

def read_csv_list(txt_file):
    """
    Reads a list of CSV filenames from a text file.

    Args:
        txt_file: The path to the text file containing the CSV filenames.

    Returns:
        A list of strings, where each string is a CSV filename.
        Returns an empty list if the file is not found or if it is empty.
    """
    try:
        with open(txt_file, 'r') as f:
            csv_files = [line.strip() for line in f]  # Read and strip whitespace
        return csv_files
    except FileNotFoundError:
        print(f"Error: Text file '{txt_file}' not found.")
        return []  # Return empty list if file not found
    except Exception as e: # Catch other possible exceptions
        print(f"An unexpected error occurred while reading the file: {e}")
        return []

def fix_csv_extensions(file_list):
    """
    Checks a list of filenames and changes the extensions to ".csv" if they are not already.

    Args:
        file_list: A list of strings, where each string is a filename.

    Returns:
        A new list of strings with the corrected extensions.  Does not modify the original list.
    """

    corrected_list = []
    for filename in file_list:
        name, ext = os.path.splitext(filename)  # Split filename and extension
        if ext.lower() != ".csv":
            corrected_filename = name + ".csv"  # Correct the extension
            corrected_list.append(corrected_filename)
            print(f"Warning: Filename '{filename}' had extension '{ext}'. Changed to '{corrected_filename}'.")
        else:
            corrected_list.append(filename)  # Keep original filename
    return corrected_list

def read_data_from_csv_files(csv_files):
    """
    Reads data from a list of CSV files into a list of Pandas DataFrames.

    Args:
        csv_files: A list of strings, where each string is a CSV filename.

    Returns:
        A list of Pandas DataFrames.  Returns an empty list if there are errors 
        reading any of the files.
    """

    dataframes = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            dataframes.append(df)
        except FileNotFoundError:
            print(f"Error: CSV file '{file}' not found.")
            return []  # Return empty list if any file is not found
        except pd.errors.ParserError as e: # Catch errors during the parsing of a file
            print(f"Error parsing file {file}: {e}")
            return [] # Return empty list if any error occurs
        except Exception as e: # Catch other possible exceptions
            print(f"An unexpected error occurred while reading file {file}: {e}")
            return [] # Return empty list if any error occurs

    return dataframes

def extract_arrays_from_dataframes(dataframes):
    """
    Extracts NumPy arrays from the second column of a list of Pandas DataFrames.

    Args:
        dataframes: A list of Pandas DataFrames.

    Returns:
        A list of NumPy arrays. Returns an empty list if the input is not a list
        or if any of the DataFrames does not have a second column or if an error
        occurs during the conversion to numpy arrays.
    """

    if not isinstance(dataframes, list):
        return []  # Return empty list if input is not a list

    arrays = []
    for df in dataframes:
        try:
            if len(df.columns) < 2:  # Check if DataFrame has at least two columns
                print("Warning: One of the dataframes has less than two columns. Skipping it.")
                continue # Skip to the next dataframe
            
            array = df.iloc[:, 1].to_numpy()  # Select second column (index 1) and convert to NumPy array
            arrays.append(array)
        except AttributeError:
            print("Warning: One of the elements of the list is not a dataframe. Skipping it.")
            continue # Skip to the next element
        except Exception as e: # Catch other possible exceptions
            print(f"An unexpected error occurred while processing one of the dataframes: {e}")
            return [] # Return empty list if any error occurs

    return arrays

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a file with options.")

    # Filename argument (required)
    parser.add_argument("filename", type=str, help="Path to the file.")

    # Last/First switch
    group_last_first = parser.add_mutually_exclusive_group() # Define a mutually exclusive group
    group_last_first.add_argument("-first", action="store_false", dest="last", help="Process first lines.") # set last = False
    group_last_first.add_argument("-last", action="store_true", help="Process last lines (default).")


    # Log/Lin switch
    group_log_lin = parser.add_mutually_exclusive_group() # Define a mutually exclusive group
    group_log_lin.add_argument("-lin", action="store_false", dest="log", help="Use linear scale.") # set log = False
    group_log_lin.add_argument("-log", action="store_true", help="Use logarithmic scale (default).")

    # Parse arguments
    args = parser.parse_args()

    # Access arguments
    filename = args.filename
    last = args.last
    log = args.log

    # Print the values to show the effect of the arguments (replace with your logic)
    print(f"Filename: {filename}")
    print(f"Last: {last}")
    print(f"Logarithmic scale: {log}")
    
    # File processing logic
    csv_files = read_csv_list(filename)  # filename is the .txt file
    if not csv_files: # If there are no csv files in the txt file stop the execution
        exit()
    dataframes = read_data_from_csv_files(fix_csv_extensions(csv_files))
    if not dataframes: # If there are no dataframes in the csv files stop the execution
        exit()
    arrays = extract_arrays_from_dataframes(dataframes)
    if not arrays: # If there are no arrays in the dataframes stop the execution
        exit()

    if last:
        reference_array = arrays[-1]  # Last array
        iref = len(arrays)-1
    else:
        reference_array = arrays[0]  # First array
        iref = 0

    rmse_values = []
    for arr in arrays:
        if log:
            rmse_val = rmse_log10(arr, reference_array)
        else:
            rmse_val = rmse(arr, reference_array)
        rmse_values.append(rmse_val)

    # Print or process the rmse_values list as needed
    for i, rmse_val in enumerate(rmse_values):
        print(f"RMSE between {csv_files[i]} and reference {csv_files[iref]}: {rmse_val}")
