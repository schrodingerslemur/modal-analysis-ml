from io import StringIO
import pandas as pd
import re

class INPParser:
    """
    INPParser is a utility class for parsing Abaqus .inp files to extract node information.
    This class provides methods to:
    - Read the contents of an Abaqus .inp file.
    - Extract the node table section from the file based on specific keywords.
    - Convert the extracted node table string into a pandas DataFrame with columns for node number and coordinates (x, y, z).
    Attributes:
        inp_file (str): Path to the .inp file to be parsed.
        contents (str): The full contents of the .inp file as a string.
        node_df (pd.DataFrame): DataFrame ['node_no', 'x', 'y', 'z']
    Methods:
        _read_file(): Reads the .inp file and returns its contents as a string.
        extract_str(inp_contents, start_keyword, end_keyword): Extracts a substring between two keywords from the file contents.
        str_to_df(contents): Converts the extracted node table string into a pandas DataFrame -> ['node_no', 'x', 'y', 'z']
    """
    def __init__(self, inp_file: str):
        self.inp_file = inp_file
        self.contents = self._read_file()
        self.node_df = self.str_to_df(self.contents)
        self.density = self.get_density(self.contents)
        self.elastic_modulus = self.get_elastic_modulus(self.contents)

    def _read_file(self) -> str:
        if self.inp_file.endswith(".inp"):
            try:
                with open(self.inp_file, "r") as file:
                    return file.read()
            except Exception as e:
                raise RuntimeError(f"Error reading file {self.inp_file}: {e}")
        else:
            raise ValueError(f"File {self.inp_file} does not have a .inp extension")

    @staticmethod
    def extract_str(inp_contents: str, start_keyword: str, end_keyword: str) -> str:
        """
        Returns the extracted node, x, y, z table string from an inp_file
        """
        start_index = inp_contents.find(start_keyword)
        end_index = inp_contents.find(end_keyword)

        start_index += len(start_keyword) + 1
        table_str = inp_contents[start_index:end_index]

        return table_str

    @staticmethod
    def str_to_df(contents: str) -> pd.DataFrame:
        """
        Returns a dataframe from the extracted table string in extract_table
        """
        start_keyword = "*NODE"
        end_keyword = "**HWCOLOR COMP"
        table = INPParser.extract_str(contents, start_keyword, end_keyword)

        node_df = pd.read_csv(
            StringIO(table),
            sep=r'[,\s]+',
            header=None,
            names=[
                'node_no',
                'x',
                'y',
                'z'
            ],
            engine='python'
        )

        return node_df
    
    def get_density(contents: str) -> float:
        """
        Extracts the density value from the .inp file contents.
        """
        density_keyword = "*DENSITY"
        density_str = INPParser.extract_str(contents, density_keyword, ",")

        try:
            return float(density_str.strip())
        except ValueError:
            raise ValueError(f"Invalid density value: {density_str.strip()}")
        
    def get_elastic_modulus(contents: str) -> float:
        """
        Extracts the elastic modulus value from the .inp file contents.
        """
        # Match *ELASTIC followed by any characters (non-greedy) until a newline
        match = re.search(r'^\*ELASTIC[^\r\n]*[\r\n]+', contents, re.MULTILINE | re.IGNORECASE)
        if not match:
            raise ValueError("Could not find *ELASTIC section in the input file.")
        elastic_modulus_keyword = match.group(0).strip()
        elastic_modulus_str = INPParser.extract_str(contents, elastic_modulus_keyword, ",")

        try:
            return float(elastic_modulus_str.strip())
        except ValueError:
            raise ValueError(f"Invalid elastic modulus value: {elastic_modulus_str.strip()}")

