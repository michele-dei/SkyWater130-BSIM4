#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NMOS Transistor Binning and Netlist Modification Script

This script processes an ngspice netlist file to modify NMOS transistor
instances by assigning them a binned model based on their width (W) and
length (L). The binning follows predefined intervals, and the modified
netlist ensures that each NMOS instance has the correct model.

Functionality:
1. Parses the netlist file to find NMOS instances.
2. Determines the appropriate bin for each NMOS instance based on W and L.
3. Updates the netlist by replacing model names with binned versions.
4. Optionally creates a backup of the original netlist before modification.

Key Features:
- Supports automatic correction of already binned NMOS instances.
- Uses regular expressions to identify and modify NMOS model assignments.
- Provides detailed error handling for missing files, incorrect values, etc.
- Command-line interface with an optional backup flag.

Usage:
$ python bin.py <netlist_file> [-b]

Arguments:
- netlist_file: Path to the ngspice netlist file.
- -b, --backup: If specified, creates a backup of the original file.

Example:
$ python bin.py my_circuit.spice -b

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

import re
import os
import shutil
import time
import argparse 

def nmos_bin(W, L):
    """
    Calculates an output value based on input parameters W and L.

    Args:
        W: Width (float), given in um.
        L: Length (float), given in um.

    Returns:
        integer: The calculated output value.

    Raises:
        ValueError: If W or L are outside the defined intervals.
    """

    def get_k(value, intervals):
        for k, (lower, upper) in intervals.items():
            if lower <= value < upper:  # Note the strict inequality on upper bound
                return k
        raise ValueError(f"Value {value} is outside the allowed intervals.")

    l_intervals = {
        0: (20, 100), 1: (8, 20), 2: (4, 8), 3: (2, 4), 4: (1, 2),
        5: (0.5, 1), 6: (0.25, 0.5), 7: (0.18, 0.25), 8: (0.15, 0.18)
    }

    w_intervals = {
        0: (7, 100), 1: (5, 7), 2: (3, 5), 3: (2, 3), 4: (1.68, 2),
        5: (1.26, 1.68), 6: (1.0, 1.26), 7: (0.84, 1.0), 8: (0.74, 0.84),
        9: (0.65, 0.74), 10: (0.64, 0.65), 11: (0.61, 0.64), 12: (0.6, 0.61),
        13: (0.58, 0.6), 14: (0.55, 0.58), 15: (0.54, 0.55), 16: (0.52, 0.54),
        17: (0.42, 0.52), 18: (0.39, 0.42), 19: (0.36, 0.39)
    }

    kl = get_k(L, l_intervals)
    kw = get_k(W, w_intervals)

    return int(kl + 9 * kw)

def modify_nmos_instances(netlist_file, nmos_bin_function, backup=False):
    """Modifies NMOS instances, handling already binned models."""

    try:
        if backup:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = f"{netlist_file}.{timestamp}"
            shutil.copy2(netlist_file, backup_file)

        with open(netlist_file, 'r') as f:
            lines = f.readlines()

    except FileNotFoundError:
        raise FileNotFoundError(f"Netlist file '{netlist_file}' not found.")
    except Exception as e:
        raise Exception(f"Error during backup of netlist file. Details: {e}")

    modified_lines = []
    nmos_pattern = r"^\s*M\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+sky130_fd_pr__nfet_01v8__model\s+l=\s*(\S+)\s+w=\s*(\S+)"
    binned_nmos_pattern = r"^\s*M\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+sky130_fd_pr__nfet_01v8__model\.(\d+)\s+l=\s*(\S+)\s+w=\s*(\S+)" # Regex for already binned models

    operations_performed = []  # Keep track of operations

    for line in lines:
        match = re.match(nmos_pattern, line)
        binned_match = re.match(binned_nmos_pattern, line)

        if match:  # Unbinned model
            try:
                L_str, W_str = match.groups()
                L_str = L_str.replace('u', '')
                W_str = W_str.replace('u', '')
                L = float(L_str)
                W = float(W_str)
                bin_number = nmos_bin_function(W, L)
                modified_model = f"sky130_fd_pr__nfet_01v8__model.{bin_number}"
                modified_line = re.sub(r"sky130_fd_pr__nfet_01v8__model", modified_model, line)
                modified_lines.append(modified_line)
                operations_performed.append(f"Binned instance: {line.strip()} -> {modified_line.strip()}")

            except ValueError as e:
                raise ValueError(f"Error parsing W or L in line: {line.strip()}. Details: {e}")
            except Exception as e:
                raise ValueError(f"Error calculating bin for line: {line.strip()}. Details: {e}")

        elif binned_match:  # Already binned model
            try:
                existing_bin, L_str, W_str = binned_match.groups()
                L_str = L_str.replace('u', '')
                W_str = W_str.replace('u', '')
                L = float(L_str)
                W = float(W_str)
                correct_bin = nmos_bin_function(W, L)

                if int(existing_bin) == correct_bin:
                    modified_lines.append(line)  # Leave unchanged if correct
                    operations_performed.append(f"Instance already binned correctly: {line.strip()}")
                else:
                    modified_model = f"sky130_fd_pr__nfet_01v8__model.{correct_bin}"
                    modified_line = re.sub(r"sky130_fd_pr__nfet_01v8__model\.\d+", modified_model, line)
                    modified_lines.append(modified_line)
                    operations_performed.append(f"Corrected binning: {line.strip()} -> {modified_line.strip()}")

            except ValueError as e:
                raise ValueError(f"Error parsing W or L in line: {line.strip()}. Details: {e}")
            except Exception as e:
                raise ValueError(f"Error calculating bin for line: {line.strip()}. Details: {e}")

        else:
            modified_lines.append(line)

    with open(netlist_file, 'w') as f:
        f.writelines(modified_lines)

    for op in operations_performed:
        print(op)  # Print operations performed
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modify NMOS instances in a netlist file.")
    parser.add_argument("netlist_file", help="Path to the ngspice netlist file.")
    parser.add_argument("-b", "--backup", action="store_true", help="Create a backup of the netlist file.") # Add backup argument
    args = parser.parse_args()

    try:
        modify_nmos_instances(args.netlist_file, nmos_bin, backup=args.backup) # Pass backup argument
        print("Netlist file modified successfully.") # Modified print statement
        if args.backup:
            print("(and backup created).")

    except (FileNotFoundError, ValueError, Exception) as e:
        print(f"Error: {e}")
