import pandas as pd

from core.parser.datParser import DATParser
from core.parser.inpParser import INPParser
    
class ModalParser:
    """
    ModalParser parses modal analysis data from DAT and INP files. It takes the mode_df from DAT files, and the
    node_df from INP files and combines them.
    
    Attributes:
        dat (DATParser): Parser for the DAT file.
        mode_table_df (pd.DataFrame): DataFrame containing mode numbers and frequencies.
        max_modes (int): Maximum mode number available.
        node_df (pd.DataFrame or None): DataFrame containing node coordinates, if provided.
    Methods:
        __call__(mode_no, include_node=False): Returns mode data for the given mode number, optionally including node coordinates.
        mode_node_df(mode_no): Returns mode data merged with node coordinates for the specified mode number.
    """
    def __init__(self, dat_file: str, inp_file: str):
        self.dat = DATParser(dat_file)
        self.node_df = INPParser(inp_file).node_df # ['node_no', 'x', 'y', 'z']

        self.mode_table_df = self.dat.get_mode_table_df() # ['mode_no', 'freq']
        self.max_modes = self.dat.mode_table_df['mode_no'].max().item()

    def __call__(self, mode_no: int):
        if mode_no < 1 or mode_no > self.max_modes:
            raise ValueError(f"mode_no must be between 1 and {self.max_modes}. Provided: {mode_no}")
        
        return self.mode_node_df(mode_no)
    
    def mode_node_df(self, mode_no):
        if self.node_df is None:
            raise ValueError("No node DataFrame loaded. Please provide an inp_file.")

        mode_df = self.mode_df(mode_no)
        merged_df = pd.merge(self.node_df, mode_df, on='node_no', how='inner')
        df = merged_df
        return df