from io import StringIO
import pandas as pd

class DATParser:
    """
    DATParser is a class for parsing .dat files generated from modal analysis outputs.
    It provides methods to extract mode tables and mode-specific displacement data
    from the file contents.
    Attributes:
        dat_file (str): Path to the .dat file to be parsed.
        contents (str): Contents of the .dat file.
        mode_table_df (pd.DataFrame): DataFrame ['mode_no', 'freq']
    Methods:
        __init__(dat_file: str):
            Initializes the DATParser with the given .dat file path, reads the file,
            and extracts the mode table DataFrame.
        _read_file() -> str:
            Reads the contents of the .dat file if it has a .dat extension.
            Raises an error if the file cannot be read or does not have the correct extension.
        extract_str(contents: str, keyword: str, delim: str ='\n\n\n') -> str:
            Extracts a substring from the contents, starting after the given keyword,
            and bounded by the specified delimiter. Used to isolate table data.
        get_mode_table_df() -> pd.DataFrame:
            Extracts the mode table from the file contents, returning a DataFrame
            with columns for mode number and frequency.
        get_mode_df(mode_number: int) -> pd.DataFrame:
            Extracts the displacement table for a specific mode number, returning a DataFrame
            with columns for node number and displacement components (U1, U2, U3) -> ['mode_no', 'U1', 'U2', 'U3']
    """

    def __init__(self, dat_file: str):
        self.dat_file = dat_file
        self.contents = self._read_file()
        self.mode_table_df = self.get_mode_table_df()

    def _read_file(self) -> str:
        if self.dat_file.endswith(".dat"):
            try:
                with open(self.dat_file, "r") as file:
                    return file.read()
            except Exception as e:
                raise RuntimeError(f"Error reading file {self.dat_file}: {e}")
        else:
            raise ValueError(f"File {self.dat_file} does not have a .dat extension")

    @staticmethod
    def extract_str(contents: str, keyword: str, delim: str ='\n\n\n') -> str:
        """
        Extracts strings consisting of only table values specific for .dat files
        """
        start_index = contents.find(keyword)
        if start_index == -1:
            raise ValueError(f"Keyword '{keyword}' not found in file.")
        start_index += len(keyword)
        remaining_text = contents[start_index:]
        search_start = 0
        count = 0
        while count != 2:
            pos = remaining_text.find(delim, search_start)
            if pos == -1:
                break
            if count == 0:
                table_start_index = pos + len(delim)
            elif count == 1:
                table_end_index = pos
            count += 1
            search_start = pos + len(delim)
        try:
            table_str = remaining_text[table_start_index:table_end_index]
        except:
            table_str = remaining_text[table_start_index:]
        return table_str

    def get_mode_table_df(self) -> pd.DataFrame:
        """
        Extracts table [mode_no, freq] from extracted string
        """
        keyword = 'E I G E N V A L U E    O U T P U T'
        table = self.extract_str(self.contents, keyword)
        mode_table_df = pd.read_csv(
            StringIO(table),
            sep=r'\s+',
            header=None,
            names=[
                'mode_no',
                'eigenvalue',
                'freq (rad/time)',
                'freq (cycles/time)',
                'generalized mass',
                'composite model damping'
            ]
        )
        mode_table_df = mode_table_df[['mode_no', 'freq (cycles/time)']].copy()
        mode_table_df.rename(columns = {'freq (cycles/time)': 'freq'}, inplace=True)
        return mode_table_df

    def get_mode_df(self, mode_number: int) -> pd.DataFrame:
        """
        Exctracts table [node_no, x, y, z] from extracted string
        """
        num_str = str(mode_number)
        keyword = f"E I G E N V A L U E    N U M B E R{num_str.rjust(6, ' ')}"
        table_content_start = self.contents.find(keyword)
        table_content = self.contents[table_content_start + len(keyword):]
        table = DATParser.extract_str(table_content, 'U3', delim='\n  \n')
        max_index = table.find('MAX') 
        if max_index == -1:
            raise Exception("Incorrect file format")
        table = table[:max_index].rstrip()
        mode_df = pd.read_csv(
            StringIO(table),
            sep=r'\s+',
            header=None,
            names=[
                'node_no',
                'U1',
                'U2',
                'U3'
            ]
        )
        return mode_df

