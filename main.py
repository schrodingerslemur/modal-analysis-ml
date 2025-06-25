import argparse

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px

from parser.modalParser import ModalParser
from analyser.modalAnalyser import ModalAnalyser

def main(dat_file, inp_file):
    model=ModalParser(dat_file, inp_file)
    analyser = ModalAnalyser(model)
    print("inplane modes:")
    print(analyser.get_inplane())
    print("checking these for outplane:")
    print(analyser.get_near_inplane())

    passed = analyser.check()

    if passed:
        print("passed") 
    else:
        print("did not pass")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run modal analysis.")
    parser.add_argument("-dat", "--dat_file", required=True, help="Path to the .dat file")
    parser.add_argument("-inp", "--inp_file", required=False, help="Path to the .inp file (optional)")
    args = parser.parse_args()

    dat_file = args.dat_file
    inp_file = args.inp_file

    main(dat_file, inp_file)

"""# dat:..\data\03_V363\03_V363_Rotor.dat
..\data\04_V769\04_V769_Rotor.dat
..\data\05_V363\05_V363_Rotor_dsg2.dat
..\data\C346RS_10Jun\C346RS_frnt_rotor_modal_separation_10Jun25.dat
..\data\V801_17Jun\V801_frnt_rotor_modal_separation_17Jun25.dat
""" 
