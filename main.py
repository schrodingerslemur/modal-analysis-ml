import sys
import os 

from io import StringIO
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px

from parser.modalParser import ModalParser
from analyser.modalAnalyser import ModalAnalyser
import argparse

def main(dat_file, inp_file):
    print(inp_file)
    exit()
    model=ModalParser(dat_file, inp_file)

    analyser = ModalAnalyser(model)
    print(model.mode_table_df)
    print(analyser.get_inplane())
    print(analyser.get_inrange_inplane())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run modal analysis.")
    parser.add_argument("-dat", "--dat_file", required=True, help="Path to the .dat file")
    parser.add_argument("-inp", "--inp_file", required=False, help="Path to the .inp file (optional)")
    args = parser.parse_args()

    dat_file = args.dat_file
    inp_file = args.inp_file

    main(dat_file, inp_file)