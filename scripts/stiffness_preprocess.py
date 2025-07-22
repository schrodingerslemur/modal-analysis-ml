
import argparse

from pathlib import Path

from config import DATADIR
from core.preprocessing.io.create_h3d import create_h3d_from_odb

def main(inp_dir, odb_dir, dat_dir, output_dir, config_file, file_range=None):
    # Create global hooks
    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert odb to h3d 
    for odb_file in odb_dir.glob("*.odb"):
        if file_range and (int(odb_file.stem) < file_range[0] or int(odb_file.stem) > file_range[1]):
            continue
        output_path = str(output_dir / f"{odb_file.stem}.h3d")
        create_h3d_from_odb(str(odb_file), output_path, config_file)

if __name__ == "__main__":
    data_dir = Path(DATADIR)
    inp_dir = data_dir / "inp"
    dat_dir = data_dir / "dat"
    odb_dir = data_dir / "odb"
    dataset_dir = data_dir / "datasets"

    config_file = str(dataset_dir / "config.cfg")
    parser = argparse.ArgumentParser(description="Preprocess modal analysis data.")
    parser.add_argument('--range', type=int, nargs=2, metavar=('START', 'END'), help='range of files to process (start end)', required=False)
    args = parser.parse_args()

    # If user wants to process just one file, pass the same value for start and end in --range
    # Example: --range 1 1 will process only file 1
    main(inp_dir, odb_dir, dat_dir, dataset_dir, config_file, file_range=args.range if args.range else None)