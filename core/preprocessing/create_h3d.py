import subprocess
from config import HVTRANS

def create_h3d_from_odb(input_file, output_file, config_file):
    assert input_file.lower().endswith('.odb'), "input_file must end with .odb"
    assert output_file.lower().endswith('.h3d'), "output_file must end with .h3d"
    assert config_file.lower().endswith('.cfg'), "config_file must end with .cfg"

    args = [
        "-c", config_file,
        input_file,
        input_file,
        "-o", output_file
    ]

    # Combine the executable and arguments
    cmd = [HVTRANS] + args

    # Run the command
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Output:", result.stdout)
        print("Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e)
        print("Output:", e.stdout)
        print("Errors:", e.stderr)