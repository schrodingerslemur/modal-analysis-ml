import argparse

from core.parser.modalParser import ModalParser
from core.analyser.modalAnalyser import ModalAnalyser

def main(dat_path, inp_path):
    model=ModalParser(dat_path, inp_path)
    analyser = ModalAnalyser(model)
    passed = analyser.check()

    if passed:
        print("passed") 
    else:
        print("did not pass")

    output = {
        "Inplane modes": analyser.inplane_modes,
        "The following were checked for outplane because they were within 300 Hz": analyser.near_inplane,
        "Outplane modes": analyser.outplane_modes,
        "Pass": passed
    }

    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run modal analysis.")
    parser.add_argument("-dat", "--dat_path", required=True, help="Path to the .dat file")
    parser.add_argument("-inp", "--inp_path", required=True, help="Path to the .inp file (optional)")
    args = parser.parse_args()

    dat_path = args.dat_path
    inp_path = args.inp_path

    main(dat_path, inp_path)

