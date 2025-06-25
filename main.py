import sys
import os 

from io import StringIO
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px


from parser.modalParser import ModalParser
from analyser.modalAnalyser import ModalAnalyser

dat_file = "../data/C346RS_10Jun/C346RS_frnt_rotor_modal_separation_10Jun25.dat"
inp_file = "../data/C346RS_10Jun/C346RS_frnt_rotor_modal_separation_10Jun25.inp"
model=ModalParser(dat_file, inp_file)

analyser = ModalAnalyser(model)
print(analyser.get_inplane())