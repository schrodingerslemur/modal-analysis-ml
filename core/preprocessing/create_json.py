import json
import os
import pandas as pd

from core.parser.inpParser import INPParser
from core.parser.datParser import DATParser

# For global hooks
def create_json_from_inp(inp_file, dest_file):
    assert(inp_file.endswith(".inp"), "Source file must be a .inp file")
    assert(dest_file.endswith(".json"), "Destination file must be a .json file")

    inp_parser = INPParser(inp_file)
    data = [
        {
            "label": "E",
            "data": [inp_parser.elastic_modulus]
        },
        {
            "label": "rho",
            "data": [inp_parser.density]
        }
    ]

    json_output = json.dumps(data, indent=4)

    # Create and write to file
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    with open(dest_file, "w") as f:
        f.write(json_output)

    return json_output

# For results
def create_json_from_dat(dat_file, dest_file):
    assert(dat_file.endswith(".dat"), "Source file must be a .dat file")
    assert(dest_file.endswith(".json"), "Destination file must be a .json file")

    parser = DATParser(dat_file)
    data = []
    for i in range(1, 51):
        freq = parser.get_freq(i)
        data.append({
            "label": f"Mode {i} Frequency",
            "type": "vector",
            "data": [freq]
        })

    json_output = json.dumps(data, indent=4)

    # Create and write to file
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    with open(dest_file, "w") as f:
        f.write(json_output)

    return json_output