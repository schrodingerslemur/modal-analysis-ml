import argparse

from src.parser.modalParser import ModalParser
from src.analyser.modalAnalyser import ModalAnalyser

def main(dat_file, inp_file):
    model=ModalParser(dat_file, inp_file)
    analyser = ModalAnalyser(model)
    passed = analyser.check(tangential=True)

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

