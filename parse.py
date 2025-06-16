import sys
from io import StringIO
import numpy as np
import pandas as pd

# TODO: 
# - Store results in csv if optioned
# - Add option for directory

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

def get_U_inplane(mode_df):
    U1_sum = mode_df['U1'].sum()
    U3_sum = mode_df['U3'].sum()
    return np.sqrt(U1_sum**2 + U3_sum**2).item()

def get_U_outplane(mode_df):
    return mode_df['U2'].sum().item()

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

def contains_node(mode_df, n, threshold=10**-2, lower_p_thres=0, upper_p_thres=0.011):
    mode_df['abs_sum_xyz'] = (mode_df['U1'] + mode_df['U2'] + mode_df['U3']).abs()
    zero_proportion = (mode_df['abs_sum_xyz'] < threshold).sum()/len(mode_df)
    print(n, zero_proportion)
    return lower_p_thres <= zero_proportion <= upper_p_thres
    
def main(filename, num_samples, threshold):
    # filename = "C346RS_frnt_rotor_modal_separation_10Jun25.dat"
    with open(filename, "r") as file:
        contents = file.read()

    mode_table_df = get_mode_table_df(contents)
    max_modes = mode_table_df['mode_no'].max().item()

    inplane = []
    outplane = []
    for mode_number in range(1, max_modes+1):
        mode_df = get_mode_df(contents, mode_number)
        U_inplane = get_U_inplane(mode_df)
        U_outplane = get_U_outplane(mode_df)

        inplane.append(U_inplane)
        outplane.append(U_outplane)
    
    in_arr = np.array(inplane)
    out_arr = np.array(outplane)

    # For checking
    df = pd.DataFrame({'in_arr': in_arr, 'out_arr': out_arr})
    df['mode_no'] = df.index + 1
    df['freq'] = mode_table_df['freq']
    df.set_index('mode_no', inplace=True)
    print(df)

    top_inplane_indexes = np.argsort(in_arr)[-num_samples:][::-1] + 1 
    top_outplane_indexes = np.argsort(out_arr)[-num_samples:][::-1] + 1

    print(f"Top inplane modes: {top_inplane_indexes.tolist()}")
    print(f"Top outplane modes: {top_outplane_indexes.tolist()}\n")

    inplane_freqs = mode_table_df[mode_table_df['mode_no'].isin(top_inplane_indexes)]['freq'].tolist()
    outplane_freqs = mode_table_df[mode_table_df['mode_no'].isin(top_outplane_indexes)]['freq'].tolist()

    print("Inplane frequencies: ", inplane_freqs)
    print("Outplane frequencies: ", outplane_freqs, "\n")

    check_limit(inplane_freqs, outplane_freqs, threshold=threshold)

if __name__ == "__main__":
    # Usage: python parse.py <.dat file path> <# of top samples> <threshold for inplane - outplane>
    # Example: python parse.py C346RS_frnt_rotor_modal_separation_10Jun25.dat 5 300
    filename = sys.argv[1]
    num_samples = int(sys.argv[2])
    threshold = int(sys.argv[3])
    main(filename, num_samples, threshold)
