# from mpl_toolkits.mplot3d import Axes3D
# import matplotlib.pyplot as plt
import plotly.express as px

import pandas as pd
import numpy as np
import argparse

from core.parser.modalParser import ModalParser

def main(dat_path, inp_path, mode_no):
    model = ModalParser(dat_path, inp_path)
    mode_no = int(mode_no)
    df = model(mode_no, include_node=True)
    df['resultant'] = np.sqrt(df['U1']**2 + df['U2']**2 + df['U3']**2)

    custom_colorscale = [
        [0.0, '#00008B'],  # dark blue
        [0.5, '#FFFF00'],  # yellow
        [1.0, '#FF0000'],  # red
    ]

    min_val = min(df['x'].min(), df['y'].min(), df['z'].min())
    max_val = max(df['x'].max(), df['y'].max(), df['z'].max())

    fig = px.scatter_3d(
        df,
        x='x',
        y='y',
        z='z',
        color='resultant',
        color_continuous_scale=custom_colorscale,
        size_max=10,
        hover_data=['node_no', 'resultant']
    )

    fig.update_layout(
        title=f"Mode number ({mode_no})",
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            xaxis=dict(range=[min_val, max_val]),
            yaxis=dict(range=[min_val, max_val]),
            zaxis=dict(range=[min_val, max_val]),
        )
    )

    fig.show(renderer='browser')

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run modal analysis.")
    parser.add_argument("-dat", "--dat_path", required=True, help="Path to the .dat file")
    parser.add_argument("-inp", "--inp_path", required=True, help="Path to the .inp file (optional)")
    parser.add_argument("-mode", "--mode", required=True, help="Mode number to plot")
    args = parser.parse_args()

    dat_path = args.dat_path
    inp_path = args.inp_path
    mode = args.mode

    main(dat_path, inp_path, mode)
