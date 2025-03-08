#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 17:01:51 2025

fetch_nmos_char.py

This script extracts ID(VG) characteristics from an IV measurement data file
for a MOSFET transistor. It filters the data for a specific VDS value,
extracts VG and ID, and saves the results to a CSV file.  It also includes
error handling for file operations and provides command-line execution.

Author: Michele Dei
License: Apache License 2.0

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
"""

import numpy as np
import matplotlib.pyplot as plt  # Although imported, it is not used. Remove if not needed.
import csv
import os
import argparse
import requests

def load_data(filename):
    """Loads data from a text file into a NumPy array."""
    try:
        data = []
        with open(filename, 'r') as f:
            for line in f:
                data.append([float(x) for x in line.strip().split()])
        return np.array(data)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except ValueError:
        print(f"Error: Invalid data format in '{filename}'.")
        return None

def extract_rows_by_first_column_value(array, value):
    """Extracts rows where the first column matches the specified value."""
    return array[array[:, 0] == value]

def write_data_to_csv(data, filename):
    """Writes data to a CSV file."""
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["V", "I"])
            for row in data:
                writer.writerow(row[:2])
        print(f"Output saved to '{filename}'.")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract ID(VG) characteristics.")
    parser.add_argument("vds", type=float, help="VDS value to filter (V).")
    parser.add_argument("-o", "--output", type=str, default="output.csv", help="Output CSV filename.")
    parser.add_argument("-d", "--directory", type=str, default="tests", help="Directory containing the data file.")
    parser.add_argument("-f", "--file", type=str, default="sky130_fd_pr__nfet_01v8__iv.data", help="Data filename.")

    args = parser.parse_args()

    directory_path = args.directory
    file = args.file
    filename = os.path.join(directory_path, file)
    output_filename = args.output

    # Check if output file exists and ask to overwrite
    if os.path.exists(output_filename):
        overwrite = input(f"File '{output_filename}' already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            exit()

    # Check if input file exists, download if not, after user confirmation
    if not os.path.exists(filename):
        download = input(f"File '{filename}' not found. Download from GitHub? (y/n): ")
        if download.lower() == 'y':
            url = f"https://raw.githubusercontent.com/google/skywater-pdk-libs-sky130_fd_pr/main/cells/nfet_01v8/tests/{file}"
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raise an exception for bad status codes

                os.makedirs(directory_path, exist_ok=True) # Create the directory if it does not exists

                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"File '{filename}' downloaded successfully.")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading file: {e}")
                exit()
        else:
            print("File not found and download cancelled.")
            exit()

    data = load_data(filename)
    if data is None:
        exit()

    data_filtered = extract_rows_by_first_column_value(data, args.vds)
    V = data_filtered[:, 3]
    I = data_filtered[:, 1]
    data_new = np.stack((V, I), axis=1)
    write_data_to_csv(data_new, output_filename)
