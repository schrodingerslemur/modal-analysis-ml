# Modal Analysis Tool

This tool runs modal analysis on your data files. Data files are in the form of .dat and .inp files which, as a whole, provide the x, y, and z displacement and position vectors for a node of a given mode. The tool then classifies in-plane and out-of-plane modes for a given CAD using the following mathematics:

For demonstration, x, y, and z are positional vectors and U1, U2, and U3 are displacement vectors.
### In-plane modes
In-plane modes have to be 
- Tangential
- Non-rigid
- Above a certain in-plane displacement threshold
  
#### Tangential
<p align="center">
  <img src="https://github.ford.com/BHENDRAT/modal-analysis/assets/81602/378acba4-6411-4723-b1be-07bce6cf36b5" width="200"/>
</p>

Unit vectors:

$$
\hat{\mathbf{z}} = \langle 0, 1, 0 \rangle
$$

$$
\hat{\mathbf{r}} = \frac{\langle x, y, z \rangle}{\|\langle x, y, z \rangle\|}
$$

$$
\hat{\mathbf{T}} = \hat{\mathbf{z}} \times \hat{\mathbf{r}}
$$

Projection of displacement onto tangential and radial axis:

$$
T = \langle U_1, U_2, U_3 \rangle \cdot \hat{\mathbf{T}}
$$

$$
R = \langle u_1, U_2, U_3 \rangle \cdot \hat{\mathbf{r}}
$$

Energy in tangential and radial axis:

$$
E_T = \|T\|^2
\quad , \quad
E_R = \|R\|^2
$$

$$
\text{Tangential} =
\begin{cases}
\text{True}, & \frac{E_T}{E_R} > 2.0 \\
\text{False}, & \text{otherwise}
\end{cases}
$$

#### Rigid rotation

$$
r_{\text{len}} = \sqrt{r_x^2 + r_z^2}
$$

<p align="center">
  <img src="https://latex.codecogs.com/svg.image?\hat{t}_x=\frac{r_z}{r_{\text{len}}},\quad\hat{t}_z=-\frac{r_x}{r_{\text{len}}}" />
</p>

Tangential displacement component:

$$
u_t = U_1 \cdot \hat{t}_x + U_3 \cdot \hat{t}_z
$$

Root mean square of tangential displacement:

$$
\text{RMS} = \sqrt{\frac{1}{n} \sum u_t^2}
$$

Rigid rotation ratio:

$$
\rho =
\begin{cases}
0, & \text{if } \text{RMS} = 0 \\
\frac{|\overline{u_t}|}{\text{RMS}}, & \text{otherwise}
\end{cases}
$$

Rigid flag condition:

$$
\text{flag} =
\begin{cases}
\text{True}, & \rho > \text{threshold} \\
\text{False}, & \text{otherwise}
\end{cases}
$$

#### Minimum displacement

$$
\sum \left(U_1^2 + U_3^2\right) > 2 \cdot \mathrm{mean}\left(U_1^2 + U_3^2\right)
$$

### Out-of-plane modes
Out of plane proportion greater than 90%

$$
\frac{U_2^2}{U_1^2 + U_3^2} > 90\%
$$

# For development/updating purposes:
# Setup
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

# Usage
## GUI
1. Enter repository and enter this in terminal:
```bash
python -m backend.app
```
2. Go to [local host port 5000](http://localhost:5000).

## Command-Line
```bash
python -m scripts.main -dat <path_to_dat_file> -inp <path_to_inp_file>
```
Example:
```bash
python -m scripts.main -dat dats\C346RS_frnt_rotor_modal_separation_10Jun25.dat -inp inps\C346RS_frnt_rotor_modal_separation_10Jun25.inp
```

## API Reference (python scripts)
This repository is structured as a module. Import everything with reference to the project root. (E.g. from core.analyser.modalAnalyser import ModalAnalyser)
### ModalParser
Converts .dat and .inp file into a pandas Dataframe with columns: \['node_no', 'x', 'y', 'z', 'U1', U2', 'U3'\]
```python
from core.parser.modalParser import ModalParser
```

To obtain DataFrame of a specific mode:
1. Initialize class instance
```python
model = ModalParser(<path to dat_file>, <path to inp_file>)
```
Example: 
```python
model = ModalParser("123.dat", "123.inp")
```

2. For `n` mode, call the model to get the DataFrame:
```python
df = model(<n>)
```
Example: 
```python
df = model(1)
```

### ModalAnalyser
Analyses the DataFrame provided by `ModalParser`
```python
from core.analyser.modalAnalyser import ModalAnalyser
model = ModalParser(<path to dat_file>, <path to inp_file>)
analyser = ModalAnalyser(model)
```

Possible methods:
- `analyser.is_tangential(<n>)`
- `analyser.get_proportions(<n>)`
- `analyser.is_rigid_rotation(<n>)`
