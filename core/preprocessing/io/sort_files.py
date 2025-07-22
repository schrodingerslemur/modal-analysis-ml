import os
import shutil

def sort_files(folder: str, inp_dir: str, dat_dir: str, odb_dir: str):
    os.makedirs(inp_dir, exist_ok=True)
    os.makedirs(dat_dir, exist_ok=True)
    os.makedirs(odb_dir, exist_ok=True)

    prefix = os.path.basename(os.path.normpath(folder))[:2]

    counters = {'inp': 1, 'dat':1, 'odb':1}

    for root, dirs, files in os.walk(folder):
        for filename in files:
            ext = filename.split('.')[-1].lower()
            src_path = os.path.join(root, filename)

            if ext in counters:
                new_filename = f"{prefix}_{counters[ext]:03d}.{ext}"
                counters[ext] += 1

                if ext == 'inp':
                    dest_path = os.path.join(inp_dir, new_filename)
                elif ext == 'dat':
                    dest_path = os.path.join(dat_dir, new_filename)
                else:  # odb
                    dest_path = os.path.join(odb_dir, new_filename)

                shutil.move(src_path, dest_path)
                print(f"Moved {src_path} to {dest_path}")
