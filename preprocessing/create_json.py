import json

from core.parser.inpParser import INPParser
import os

def create_json_from_inp(inp_file, dest_file):
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