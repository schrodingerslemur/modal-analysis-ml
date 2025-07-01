# Modal Analysis Tool

This tool runs modal analysis on your data files.

TODO: 
- Check on 5 more models
- API reference
- App run reference
- Push backend
- Implement CD/CI pipeline

## Setup
### Github
1. Open terminal and setup your ssh keys:
```bash
ssh-keygen -t ed25519
```
You will be prompted with entering a file to save key in, and passphrases. Don't type anything and just keep pressing enter until there are no more prompts. (Should be 3x)

2. Enter this to retrieve your public keys. Copy the entire output (from 'ssh-rsa' all the way until the end)
```bash
cat ~/.ssh/id_rsa.pub
```

3. Open [this site](https://github.ford.com/settings/keys). Press `New SSH Key`, add any `Title`, and paste the public key into the `Key` portion. Hit `Save`.

### Requirements
1. Clone the repository
```bash
git clone git@github.ford.com:BHENDRAT/modal-analysis.git
```

2. Create a virtual environment
```bash
pip install virtualenv
python -m virtualenv env
```

3. Activate virtual environment
If you are on Windows: 
```bash
./env/Scripts/activate.ps1
```
On mac: (might be wrong, look for online documentation for activating virtual env. Likewise for Linux)
```bash
source env/Scripts/activate
```

4. Install necessary libraries
```bash
cd modal-analysis
pip install -r requirements.txt
```

## Usage
### GUI
1. Enter repository and enter this in terminal:
```bash
python -m backend.app
```
2. Go to [local host port 5000](http://localhost:5000).

### Command-Line
```bash
python -m scripts.main -dat <path_to_dat_file> -inp <path_to_inp_file>
```
Example:
```bash
python -m scripts.main -dat dats\C346RS_frnt_rotor_modal_separation_10Jun25.dat -inp inps\C346RS_frnt_rotor_modal_separation_10Jun25.inp
```

## API Reference
