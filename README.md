# SkyWater130-BSIM4
# BSIM4 NMOS Model and Characterization Scripts

This repository contains a pure BSIM4 model of the SkyWater SKY130 NMOS transistor, derived from the mixed BSIM4/BSIM3 model available in the SkyWater PDK.  It also includes Python scripts used for data processing and analysis.

## License
================================================================================
                            LICENCE INFO
================================================================================

This work is licensed under the Apache License, Version 2.0. See the LICENSE file for details.

This model is derived from the SkyWater SKY130 NMOS transistor model available at:
https://github.com/google/skywater-pdk-libs-sky130_fd_pr/blob/main/cells/nfet_01v8/sky130_fd_pr__nfet_01v8__tt.pm3.spice

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

## Usage
================================================================================
                            USAGE INSTRUCTIONS
================================================================================

1. Running a Single Simulation
------------------------------
To run an ngspice simulation on a .cir netlist file while automatically handling 
model binning and data processing, use:

    ./ng <netlist_file.cir> [-csv] [-pdf]

Example:
    ./ng test01.cir -csv -pdf

This will:
- Modify the netlist (binning NMOS instances using bin.py).
- Run the simulation using ngspice.
- Convert output to CSV (raw2csv.py).
- Generate a plot (if -pdf is specified, csv_plotter.py is executed).

Output files:
- test01.csv  -> Processed CSV file with simulation results.
- test01.pdf  -> PDF plot of the simulation output.

--------------------------------------------------------------------------------

2. Comparing Multiple Simulations
---------------------------------
If you have multiple netlists (.cir files) and want to compare their results:

Step 1: Create a `tests.txt` file listing the netlists to compare:
    test01.cir
    test02.cir
    test03.cir

Step 2: Run the comparison scripts:

- Numerical comparison (RMSE-based):
    ./csv_comp.py tests.txt
  This computes the root mean square error (RMSE) between the test cases and 
  a reference dataset (output.csv).

- Visual comparison (plots):
    ./csv_plotter.py tests.txt
  This generates `tests.pdf`, a multi-plot visualization of all listed CSV files.

--------------------------------------------------------------------------------

3. Individual Script Details
----------------------------
git_nmos.py    - Fetch the NMOS characteristics from github (https://raw.githubusercontent.com/google/skywater-pdk-libs-sky130_fd_pr/main/cells/nfet_01v8/tests/sky130_fd_pr__nfet_01v8__iv.data).
	         When VDS value is given (default 1.2), creates output.csv containing the ID(VG) characteristics at fixed VDS.
bin.py         - Bins NMOS transistors based on W/L values in the netlist. Updates .cir files 
                 with the correct BSIM4 model bin.

raw2csv.py     - Converts ngspice .raw output files to properly formatted CSVs.

csv_plotter.py - Reads multiple .csv files and generates plots in PDF format.

csv_comp.py    - Computes RMSE (root mean square error) between CSV data and a reference file.

ng (Bash)      - Automates the simulation: Runs binning, ngspice, CSV conversion, and plotting.

--------------------------------------------------------------------------------

4. Customizing Output
---------------------
- If you only want raw data, run:
      ./ng test01.cir

- If you want CSV conversion but no plots, use:
      ./ng test01.cir -csv

- If you want plots but not CSVs, use:
      ./ng test01.cir -pdf
      

## Folder content
================================================================================
                            FOLDER CONTENT
================================================================================


Files in this folder:
========================#===========================================================================================================================
bin.py			| Python script for mos model binning. Manipulates the .cir files to associate the 
			| correct mosfet model bin, based on the W and L values of the nmos instances.
csv_comp.py		| Python script for numerical comparison (based on root mean square error) of the .cir
			| files outpus (.csv) against the output.csv file (of which W and L are unknown).
			| Terminal invocation (typ.): >./csv_comp.py tests.txt 
			| tests.txt is a manually edited file containing the test (.cir files) to compare.
csv_plotter.py		| Python script for visual comparison as for csv_comp.py. Produces a PDF.
			| Terminal invocation (typ.): >./csv_plotter.py tests.txt 
git_nmos.py		| Python script for producing the original NMOS characteristics from github link. 
			| (Generates output.csv if not already present in path).
			| Terminal invocation (typ.): >./git_nmos.py 1.2
ng			| Bash script for invoking ngspice on a specific .cir file, but also performs binning 
			| (see bin.py) before invoking ngspice. 
			| Terminal invocation (typ.): >./ng test01.cir -csv -pdf
			| Produces: test01.csv and test01.pdf
output.csv		| Nmos characteristics, downloaded from: 
			| https://github.com/google/skywater-pdk-libs-sky130_fd_pr/tree/main/cells/nfet_01v8/tests
			| and elaborated to have ID(VG).
raw2csv.py		| Python script to correctly format the csv files when after invoking the ng script.
README.TXT		| This file.
sky130_fd_pr_nfet_01v8_tt_nominal_bsim4.spice
			| BSIM4 porting of the SkyWater models for 1.8 regular NMOS (typical).
			| Original models from:
			| https://github.com/google/skywater-pdk-libs-sky130_fd_pr/blob/main/cells/nfet_01v8/sky130_fd_pr__nfet_01v8__tt.pm3.spice
------------------------+---------------------------------------------------------------------------------------------------------------------------
test01.cir		| Test circuit for source grounded nmos, produces ID(VG) data for VG sweep and fixed VD.
test01.csv		| Output of invocation of: > ./ng test01.cir -csv
test01.pdf		| Output of invocation of: > ./ng test01.cir -csv -pdf
test02.cir		| .
test02.csv		| .
test02.pdf		| .
test03.cir		| .
test03.csv		| .
test03.pdf		| .
test04.cir		| .
test04.csv		| .
test04.pdf		| .
test05.cir		| .
test05.csv		| .
test05.pdf		| .
test06.cir		| .
test06.csv		| .
test06.pdf		| .
test07.cir		| .
test07.csv		| .
test07.pdf		| .
------------------------+---------------------------------------------------------------------------------------------------------------------------
tests.pdf		| PDF output of csv_plotter.py.
tests.txt		| Manually edited file list for csv_comp.py and csv_plotter.py
