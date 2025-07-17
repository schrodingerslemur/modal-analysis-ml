from pathlib import Path

from core.preprocessing.filter.plot import plot_max_disp

from config import DATADIR

if __name__ == "__main__":
    dat_path = Path(DATADIR) / "dat"
    plot_max_disp(dat_path)