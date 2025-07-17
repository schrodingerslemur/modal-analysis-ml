import os
import shutil

def sort_files(folder: str, inp_dir: str, dat_dir: str, odb_dir: str):
    os.makedirs(inp_dir, exist_ok=True)
    os.makedirs(dat_dir, exist_ok=True)
    os.makedirs(odb_dir, exist_ok=True)

    prefix = os.path.basename(os.path.normpath(folder))[:2]  # obtain model number from lowerst folder
    print(prefix)

    for filename in os.listdir(folder):
        src_path = os.path.join(folder, filename)
        ext = filename.split('.')[-1].lower()

        if ext == 'inp':
            new_filename = prefix + '.inp'
            dest_path = os.path.join(inp_dir, new_filename)

        elif ext == 'dat':
            new_filename = prefix + '.dat'
            dest_path = os.path.join(dat_dir, new_filename)

        elif ext == 'odb':
            new_filename = prefix + '.odb'
            dest_path = os.path.join(odb_dir, new_filename)

        else:
            continue  # skip other file types

        # Move and rename file
        shutil.move(src_path, dest_path)
        print(f"Moved {src_path} to {dest_path}")
