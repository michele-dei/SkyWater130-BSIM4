#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: raw2csv.py

Purpose:
--------
This script processes simulation output files from **ngspice** by merging raw data
(`.raw`) with headers (`.csv_heads`) into a properly formatted CSV file. If the
header file is missing, the script generates default column names.

Functionality:
--------------
1. **Extracts Headers:**  
   - Reads the header file (`.csv_heads`) if available.  
   - If missing, it determines the number of columns from the raw data and assigns
     default column names (`Column1, Column2, ...`).

2. **Processes Raw Data:**  
   - Reads the `.raw` file and parses it into a structured format using `pandas`.  
   - Assigns column names from the extracted headers.

3. **Saves as CSV:**  
   - The combined data (headers + raw data) is saved as a `.csv` file.

4. **Cleans Up Files (Optional):**  
   - Deletes the `.csv_heads` and `.raw` files after processing
     (this can be disabled by commenting out the removal lines).

Usage:
------
Run the script from the terminal:
    $ python raw2csv.py <path_to_circuit_file.cir>

The script assumes that:
- `<path_to_circuit_file>.csv_heads` and `<path_to_circuit_file>.raw`
  exist in the same directory.

Error Handling:
---------------
- If the `.csv_heads` file is missing, it prints a warning and assigns default column names.
- If the `.raw` file is missing or incorrectly formatted, the script reports the error and exits.
- The script includes exception handling for **file errors, parsing issues, and unexpected failures**.


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

import pandas as pd
import argparse
import os

def combine_data_and_headers(cir_file):
    """
    Combines .raw data with headers, handling missing .csv_heads.
    """

    base_name = cir_file[:-4]  # Remove ".cir"
    headers_file = f"{base_name}.csv_heads"
    raw_data_file = f"{base_name}.raw"
    output_file = f"{base_name}.csv"

    try:
        try:
            with open(headers_file, 'r') as hf:
                headers_line = hf.readline().strip()
                headers = headers_line.split(",")
        except FileNotFoundError:
            print(f"Warning: Headers file '{headers_file}' not found. Using default column names.")
            # Determine the number of columns from the raw data file.
            try:
                with open(raw_data_file, 'r') as rf:
                    first_line = rf.readline()
                    num_columns = len(first_line.split())  # Count the number of values in the first line
                    headers = [f"Column{i+1}" for i in range(num_columns)]

            except FileNotFoundError:
                print(f"Error: Raw data file '{raw_data_file}' not found.")
                return

            except Exception as e:
                print(f"An unexpected error occurred while reading the raw file: {e}")
                return

        try:
            df = pd.read_csv(
                raw_data_file,
                sep=r"\s+",
                names=headers,
                skipinitialspace=True,
                engine="python",
            )

            df.to_csv(output_file, index=False)
            print(f"Combined data and headers into {output_file}")

        except FileNotFoundError:
            print(f"Error: Raw data file '{raw_data_file}' not found.")
            return

        except pd.errors.ParserError as e:
            print(f"Error parsing raw data: {e}")
            return

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return

        # Delete .csv_heads and .raw files (optional - comment out if needed)
        try:
            if os.path.exists(headers_file): # Check if the file exists before attempting to remove it.
                os.remove(headers_file)
            os.remove(raw_data_file)
            print(f"Deleted {headers_file} and {raw_data_file}")
        except OSError as e:
            print(f"Error deleting files: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine ngspice raw data with headers.")
    parser.add_argument("cir_file", help="Path to the .cir file.")
    args = parser.parse_args()

    combine_data_and_headers(args.cir_file)
