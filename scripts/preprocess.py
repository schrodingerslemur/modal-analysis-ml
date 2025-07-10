import os
import sys
from pathlib import Path

from config import DATADIR
from core.preprocessing.create_json import create_json_from_inp, create_json_from_dat
from core.preprocessing.create_h3d import create_h3d_from_odb

def main(inp_dir, output_dir, config_file):
    # Create global hooks
    output_dir.mkdir(parents=True, exist_ok=True)

    for inp_file in inp_dir.glob("*.inp"):
        output_path = str(output_dir / f"{inp_file.stem}_inp.json")
        create_json_from_inp(str(inp_file), output_path)

    # Convert odb to h3d 
    for odb_file in odb_dir.glob("*.odb"):
        output_path = str(output_dir / f"{odb_file.stem}.h3d")
        create_h3d_from_odb(str(odb_file), output_path, config_file)

    # Create result json
    for dat_file in dat_dir.glob("*.dat"):
        output_path = str(output_dir / f"{dat_file.stem}.json")
        create_json_from_dat(str(dat_file), output_path)

    # copy to global hooks dir

#for input.h3d, need to have input_inp.json in _hooks, global_inputs_hook.py needs to be copied too
if __name__ == "__main__":
    data_dir = Path(DATADIR)
    inp_dir = data_dir / "inp"
    dat_dir = data_dir / "dat"
    odb_dir = data_dir / "odb"
    dataset_dir = data_dir / "datasets"

    config_file = str(dataset_dir / "config.cfg")
    main(inp_dir, dataset_dir, config_file)