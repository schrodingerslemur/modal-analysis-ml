from core.preprocessing.io.sort_files import sort_files
from pathlib import Path
import argparse
from config import DATADIR

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort files into inp, odb, and dat directories")
    parser.add_argument('-f', type=str, help='Folder containing inp, odb, and dat files', required=True)
    args = parser.parse_args()
    inp_dir = Path(DATADIR) / "inp"
    dat_dir = Path(DATADIR) / "dat"
    odb_dir = Path(DATADIR) / "odb"
    sort_files(args.f, inp_dir, dat_dir, odb_dir)