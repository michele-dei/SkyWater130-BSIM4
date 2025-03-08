#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 15:26:21 2025

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

Script: CSV Data Plotter for ngspice Simulations

Purpose:
--------
This script reads CSV files generated from **ngspice** simulations and plots the 
data. The script supports multiple input formats and can automatically scale the 
axes based on the magnitude of values. It also provides options to generate and 
save plots in **PDF format**.

Functionality:
--------------
1. **Input Handling:**
   - Takes as input either:
     - A **.cir file**, which is converted into the corresponding **.csv file**.
     - A **.txt file** containing a list of `.cir` filenames (each mapped to a `.csv` file).
   - Checks for missing files and prints an error message if needed.

2. **Data Processing:**
   - Reads the **CSV file(s)** and loads the numerical data into Pandas DataFrames.
   - If multiple CSV files are provided (via a `.txt` list), all datasets are plotted in 
     a single figure.

3. **Plotting:**
   - Automatically **scales the axis labels** based on the average magnitude of the data 
     (e.g., converting to nA, µA, mA).
   - Supports **alternate X/Y column structures** (e.g., X1, Y1, X2, Y2, ...).
   - Generates a **legend** based on column headers.
   - Saves the plot as a **PDF file** by default.

4. **Command-Line Arguments:**
   - `-a, --alternate` : Interprets columns as **X1, Y1, X2, Y2, ...** instead of standard **X, Y1, Y2, ...**.
   - `--no-pdf` : Disables PDF generation (default is to save plots as PDFs).

Usage:
------
Run the script from the terminal:

    $ python script.py <input_file> [-a] [--no-pdf]

Where:
- `<input_file>` can be:
  - A **.cir** file → Plots data from a single corresponding `.csv` file.
  - A **.txt** file → Reads a list of `.cir` files, converts them to `.csv`, and plots all datasets together.
- `-a, --alternate` enables **alternate X/Y plotting**.
- `--no-pdf` disables saving the plot as a PDF.

Error Handling:
---------------
- **Missing Files:** If a required `.csv` file is missing, an error is displayed.
- **Invalid File Types:** If the input file is neither `.cir` nor `.txt`, the script exits with an error.
- **Empty or Malformed CSVs:** If no valid data is found, no plot is generated.
- **Scaling Issues:** If the data magnitude is zero, axis scaling is disabled to avoid formatting errors.

"""

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

def get_csv_filename(cir_file):
    """Returns the CSV filename corresponding to the .cir file."""
    base_name = cir_file[:-4]  # Remove ".cir"
    return f"{base_name}.csv"

def get_data_from_csv(csv_file):
    """Reads data from the CSV file into a Pandas DataFrame."""
    try:
        df = pd.read_csv(csv_file)
        return df
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        return None

def auto_scale_axis(ax, data):
    """Automatically scales an axis with appropriate prefixes."""

    magnitude = np.mean(np.abs(data))  # Use mean absolute value to determine magnitude

    if magnitude == 0: # Handle the case of magnitude zero to avoid errors
        scale = 0
        prefix = ""
    elif magnitude < 1e-12:
        scale = 1e-15
        prefix = "f"
    elif magnitude < 1e-9:
        scale = 1e-12
        prefix = "p"
    elif magnitude < 1e-6:
        scale = 1e-9
        prefix = "n"
    elif magnitude < 1e-3:
        scale = 1e-6
        prefix = "u"
    elif magnitude < 1:
        scale = 1e-3
        prefix = "m"
    elif magnitude < 1e3:
        scale = 1
        prefix = ""
    elif magnitude < 1e6:
        scale = 1e3
        prefix = "k"
    elif magnitude < 1e9:
        scale = 1e6
        prefix = "M"
    elif magnitude < 1e12:
        scale = 1e9
        prefix = "G"
    else:
        scale = 1e12
        prefix = "T"  # Terrahertz

    ax.set_major_formatter(lambda x, pos: f"{x/scale:.2f}{prefix}")  # Format ticks
    return prefix

def plot_data(df_list, plot_title, alternate_xy=False, save_pdf=True, show=False):
    """Plots data from a list of DataFrames, handling alternate X/Y and PDF."""

    plt.figure(figsize=(6, 6))

    if alternate_xy:
        for df in df_list:
            x_values = df.iloc[:, ::2]
            y_values = df.iloc[:, 1::2]
    
            for i in range(len(x_values.columns)):
                x = x_values.iloc[:, i]
                y = y_values.iloc[:, i]
                plt.plot(x, y, label=f"Y{i+1}")

    else:
        for i_df, df in enumerate(df_list):
            x = df.iloc[:, 0]
            x_prefix = auto_scale_axis(plt.gca().xaxis, x)
            for i in range(1, len(df.columns)):
                y = df.iloc[:, i]
                y_prefix = auto_scale_axis(plt.gca().yaxis, y)
                plt.plot(x, y, label=df.columns[i]+f' ({i_df+1})')

    plt.xlabel(f"{df_list[0].columns[0]}")  # X-axis label. Assumes all dataframes have the same x column name
    plt.ylabel(f"Y Values")  # Y-axis label
    plt.title(plot_title)
    plt.legend()
    plt.grid(True)

    if save_pdf:
        base_name = plot_title[:-4] # Remove ".csv" or ".txt"
        pdf_file = f"{base_name}.pdf"
        with PdfPages(pdf_file) as pdf:
            plt.tight_layout()
            pdf.savefig()
        print(f"Plot saved to {pdf_file}")

    if show:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot data from CSV file(s).")
    parser.add_argument("input_file", help="Path to the .cir or .txt file.")
    parser.add_argument("-a", "--alternate", action="store_true", help="Interpret columns as X, Y1, X, Y2, ...")
    parser.add_argument("--no-pdf", action="store_false", dest="pdf", help="Do not save the plot to a PDF file.")
    args = parser.parse_args()

    input_file = args.input_file

    if input_file.endswith(".cir"):
        csv_file = get_csv_filename(input_file)
        df = get_data_from_csv(csv_file)
        if df is not None:
            plot_data([df], csv_file, args.alternate, args.pdf) # Pass a list with a single dataframe.
    elif input_file.endswith(".txt"):
        try:
            with open(input_file, 'r') as f:
                cir_files = [line.strip() for line in f]
        except FileNotFoundError:
            print(f"Error: .txt file '{input_file}' not found.")
            exit()

        df_list = []
        for cir_file in cir_files:
            csv_file = get_csv_filename(cir_file)
            df = get_data_from_csv(csv_file)
            if df is not None:
                df_list.append(df)

        if df_list:  # Check if any dataframes were successfully read
            plot_data(df_list, input_file, args.alternate, args.pdf) # plot all the dataframes in a single plot
        else:
            print("No valid data found in the input files.")
    else:
        print("Invalid input file type. Must be .cir or .txt.")
