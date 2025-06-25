from io import StringIO
import pandas as pd

class DATParser:
    def __init__(self, dat_file: str):
        self.dat_file = dat_file
        self.contents = self._read_file()
        self.mode_table_df = self.get_mode_table_df(self.contents)

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

    @staticmethod
    def get_mode_table_df(contents: str) -> pd.DataFrame:
        """
        Extracts table [mode_no, freq] from extracted string
        """
        keyword = 'E I G E N V A L U E    O U T P U T'
        table = DATParser.extract_str(contents, keyword)
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

