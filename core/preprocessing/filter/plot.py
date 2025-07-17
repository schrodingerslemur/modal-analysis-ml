import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from core.parser.datParser import DATParser

def plot_max_disp(dat_dir: Path) -> None: # Possible limitation: only using dat
    max_disp = []
    dat_files = []
    for dat_file in dat_dir.glob("*.dat"):
        parser = DATParser(str(dat_file))
        max_disp.append(parser.get_max_disp())
        dat_files.append(dat_file.stem)

    plt.scatter(dat_files, max_disp)
    plt.xlabel("Model Number")
    plt.ylabel("Max Displacement (m)")
    plt.title("Max Displacement vs Model Number")
    plt.legend()
    plt.show()