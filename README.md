# Modal Analysis Tool

This tool runs modal analysis on your data files.

## Requirements
Install requirements first:
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py -dat <path_to_dat_file> [-inp <path_to_inp_file>]
```
Example:
```bash
python main.py -dat dats\C346RS_frnt_rotor_modal_separation_10Jun25.dat
```
or
```bash
python main.py -dat dats\C346RS_frnt_rotor_modal_separation_10Jun25.dat -inp inps\C346RS_frnt_rotor_modal_separation_10Jun25.inp
```
