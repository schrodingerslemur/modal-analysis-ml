import sys
from io import StringIO
import numpy as np
import pandas as pd

# TODO: 
# - Figure out threshold
# - Figure out order of magnitude for generalization

### INP FILES: 
def extract_inp_table(inp_contents: str, start_keyword: str, end_keyword: str):
    start_index = inp_contents.find(start_keyword)
    end_index = inp_contents.find(end_keyword)

    start_index += len(start_keyword) + 1
    extracted_text = inp_contents[start_index:end_index]

    return extracted_text

def get_node_df(inp_contents: str): # from inp file
    start_keyword = "*NODE"
    end_keyword = "**HWCOLOR COMP"
    table = extract_inp_table(inp_contents, start_keyword, end_keyword)

    node_table_df = pd.read_csv(
        StringIO(table),
        sep=r'[,\s]+',
        header=None,
        names=[
            'node_no',
            'x',
            'y',
            'z'
        ]
    )

    return node_table_df

### DAT FILES:
def extract_table(contents: str, keyword: str, delim: str ='\n\n\n') -> str:
    """
    Extracts strings consisting of only table values specific for .dat files
    """
    # Find keyword index
    start_index = contents.find(keyword)
    if start_index == -1:
        raise ValueError(f"Keyword '{keyword}' not found in file.")
    
    start_index += len(keyword)
    
    # Start remaining text after keyword
    remaining_text = contents[start_index:]
    
    # Find 2 occurrences of delim
    positions = []
    search_start = 0
    
    count = 0
    while count != 2:
        pos = remaining_text.find(delim, search_start)
        if pos == -1:
            break
        if count == 0:
            table_start_index = pos + 3
        elif count == 1:
            table_end_index = pos
            
        count += 1
        search_start = pos +3
    
    try:
        extracted_text = remaining_text[table_start_index:table_end_index]
    except:
        extracted_text = remaining_text[table_start_index:]
    
    return extracted_text

def get_mode_table_df(contents: str):
    keyword = 'E I G E N V A L U E    O U T P U T'
    table = extract_table(contents, keyword)

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

def get_mode_df(contents, mode_number):
    num_str = str(mode_number)
    keyword = f"E I G E N V A L U E    N U M B E R{num_str.rjust(6, ' ')}"
    table_content_start = contents.find(keyword)
    table_content = contents[table_content_start + len(keyword):]

    table = extract_table(table_content, 'U3', delim='\n  \n')

    max_index = table.find('MAX') 
    if max_index == -1:
        raise Exception("Incorrect file format")
    table = table[:max_index].rstrip()

    # print(table)
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

### LOGICAL FUNCTIONS:
def check_limit(l1, l2, threshold=300):
    errors = 0
    for a in l1:
        for b in l2:
            if abs(a - b) < threshold:
                print(f"Failed because inplane ({a}) is {threshold} within outplane ({b})")
                errors += 1
    
    print(f"Found {errors} error(s)")

def get_proportions(mode_df, n):
    # only use positive y values
    mode_df = mode_df[mode_df['U2'] >= 0].copy()
    
    mode_df['sq_x'] = mode_df['U1']**2
    mode_df['sq_y'] = mode_df['U2']**2
    mode_df['sq_z'] = mode_df['U3']**2
    
    sumsq_x = mode_df['sq_x'].sum()
    sumsq_y = mode_df['sq_y'].sum()
    sumsq_z = mode_df['sq_z'].sum()

    total_energy = sumsq_x + sumsq_y + sumsq_z

    oop = (sumsq_y) / total_energy
    ip = (sumsq_x + sumsq_z) / total_energy

    # print(f"Mode {n} has OOP: {oop*100}%, IP: {ip*100}%.\n")
    return oop*100, ip*100, sumsq_x, sumsq_y, sumsq_z

def contains_node(mode_df, threshold=7, lower_p_thres=0):
    mode_df['resultant'] = np.sqrt(mode_df['U1']**2 + mode_df['U2']**2 + mode_df['U3']**2)
    zero_proportion = (mode_df['resultant'] < threshold).sum()/len(mode_df)
    return zero_proportion > lower_p_thres

def get_inplane(contents, max_modes):
    inplane_preds = []
    tupled_inplane_preds = []

    for mode_number in range(1, max_modes+1):
        mode_df = get_mode_df(contents, mode_number)
        oop, ip, x, y, z = get_proportions(mode_df, mode_number)

        print(f"Mode Number: {mode_number}, OOP: {oop}, IP: {ip}, x+z: {x+z}")
        if ip > 96 and (x+z) > 100000: ### TODO: Adjust this number
            if contains_node(mode_df):
                inplane_preds.append(mode_number)

                if tupled_inplane_preds and (mode_number - 1 in tupled_inplane_preds[-1]):
                    # Pop the last tuple, extend it, and re-append
                    last_tuple = tupled_inplane_preds.pop()
                    new_tuple = last_tuple + (mode_number,)
                    tupled_inplane_preds.append(new_tuple)
                else:
                    # Start a new tuple group
                    tupled_inplane_preds.append((mode_number,))
                    
    return inplane_preds, tupled_inplane_preds

def search_oop(contents, start, inplane, reverse=False, max_modes = 136):
    """
    Linear search
    """
    checks = 0 # if checks > 5, then take largest
    if reverse:
        inc = -1
    else:
        inc = 1

    oop_values = []
    while (checks <= 5):
        checks += 1
        start += inc
        if start == 0 or start == max_modes or start in inplane:
            break

        mode_df = get_mode_df(contents, start)
        oop, _, _, _, _ = get_proportions(mode_df, start)

        if oop > 95:
            return start
        else:
            oop_values.append((start, oop))

    if len(oop_values) == 0:
        return None ### TODO: Ensure correct logic
    elif len(oop_values) < 3:
        if all(value[-1] < 90 for value in oop_values):
            return None
    
    largest_oop = max(oop_values, key=lambda x: x[1])
    return largest_oop[0]

def get_outplane(contents, inplane, tupled_inplane: list[tuple], max_modes):
    outplane_preds = []
    
    for i in range(len(tupled_inplane)):
        elem = tupled_inplane[i]
        # for elem[0]
        pred_reverse = search_oop(contents, elem[0], inplane, reverse=True, max_modes=max_modes)
        if pred_reverse: # ensure not None
            outplane_preds.append(pred_reverse)
        
        # for elem[-1]
        pred_forward = search_oop(contents, elem[-1], inplane, reverse=False, max_modes=max_modes)
        if pred_forward:
            outplane_preds.append(pred_forward)
    
    return outplane_preds

def plot_sum_graph(mode_no):
    node_df = get_node_df(inp_contents)
    mode_df = get_mode_df(contents, mode_no)
    mode_df['resultant'] = np.sqrt(mode_df['U1']**2 + mode_df['U2']**2 + mode_df['U3']**2)
    sum_df = mode_df[['node_no','resultant']] # node and sum
    merged_df = pd.merge(node_df, sum_df, on='node_no', how='inner')
    df = merged_df
    
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
    
def main(dat_file):
    # dat_file = "C346RS_frnt_rotor_modal_separation_10Jun25.dat"
    with open(dat_file, "r") as file:
        contents = file.read()

    mode_table_df = get_mode_table_df(contents)
    max_modes = mode_table_df['mode_no'].max().item()

    inplane_preds, tupled_inplane_preds = get_inplane(contents, max_modes)
    outplane_preds = get_outplane(contents, inplane_preds, tupled_inplane_preds, max_modes)

    outplane_preds = sorted(list(set(outplane_preds)))

    inplane_labels = [32, 33, 46, 47, 68, 69, 100, 101]
    outplane_labels = [29, 36, 45, 48, 65, 71, 94, 105]

    print(f"inplane predictions: {inplane_preds}")
    # print(f"inplane labels: {inplane_labels}")

    print(f"outplane predictions: {outplane_preds}")
    # print(f"outplane labels: {outplane_labels}")

if __name__ == "__main__":
    # Usage: python parse.py <.dat file path> 
    # Example: python parse.py data\C346RS_10Jun\C346RS_frnt_rotor_modal_separation_10Jun25.dat
    # python parse.py 'data/V801_17Jun/V801_frnt_rotor_modal_separation_17Jun25 (1).dat'
    dat_file = sys.argv[1]
    main(dat_file)
