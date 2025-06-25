import pandas as pd

from parser.datParser import DATParser
from parser.inpParser import INPParser
    
class ModalParser:
    def __init__(self, dat_file: str, inp_file: str = None):
        self.dat = DATParser(dat_file)
        # Columns: mode_no, freq
        self.mode_table_df = self.dat.get_mode_table_df()
        self.max_modes = self.dat.mode_table_df['mode_no'].max().item()

        if inp_file:
            # Columns: node_no, x, y, z
            self.node_df = INPParser(inp_file).node_df
        else:
            self.node_df = None

    def __call__(self, mode_no: int, include_node: bool = False):
        if mode_no < 1 or mode_no > self.max_modes:
            raise ValueError(f"mode_no must be between 1 and {self.max_modes}. Provided: {mode_no}")
        
        if include_node:
            return self.mode_node_df(mode_no)
        else:
            return self.mode_df(mode_no)
    
    def mode_df(self, mode_no: int):
        return self.dat.get_mode_df(mode_no)

    def mode_node_df(self, mode_no):
        if self.node_df is None:
            raise ValueError("No node DataFrame loaded. Please provide an inp_file.")

        mode_df = self.mode_df(mode_no)
        merged_df = pd.merge(self.node_df, mode_df, on='node_no', how='inner')
        df = merged_df
        return df