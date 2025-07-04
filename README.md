# Modal Analysis Tool

This tool runs modal analysis on your data files. Data files are in the form of .dat and .inp files which, as a whole, provide the x, y, and z displacement and position vectors for a node of a given mode. The tool then classifies in-plane and out-of-plane modes for a given CAD using the following mathematics:

For demonstration, x, y, and z are positional vectors and U1, U2, and U3 are displacement vectors.

## Deployed Applications
The Modal Analysis Tool is deployed and accessible at the following locations:

### HPC Deployment
- **Application URL**: https://mach1.hpc.ford.com/rpadma10/modal-analysis/

### CaaS Deployment  
- **Application URL**: https://modal-analysis.apps.pp101.caas.gcp.ford.com/

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

2. Install uv package manager

**On macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Note:** After installation, ensure uv is added to your PATH. You may need to restart your terminal or source your shell configuration file.

3. Install dependencies and create virtual environment
   
```bash
cd modal-analysis
uv sync
```

This will automatically create a virtual environment and install all necessary packages from the `pyproject.toml` and `uv.lock` files.

4. Activate the virtual environment
   
```bash
source .venv/bin/activate
```

# Usage
## GUI
1. Enter repository and run the app:
```bash
uv run python -m backend.app
```
2. Go to [local host port 5000](http://localhost:5000).

## Command-Line
```bash
uv run python -m scripts.main -dat <path_to_dat_file> -inp <path_to_inp_file>
```
Example:
```bash
uv run python -m scripts.main -dat dats\C346RS_frnt_rotor_modal_separation_10Jun25.dat -inp inps\C346RS_frnt_rotor_modal_separation_10Jun25.inp
```

## HPC Deployment
For HPC deployment, users need to have an HPC account.

### HPC Account Setup
Request an HPC account here: https://fcp.ford.com/hpc

The same login can be used to access HPC's image registry `harbor.hpc.ford.com`.

### Image Registry Access
The modal-analysis project can be accessed here: https://harbor.hpc.ford.com/harbor/projects/4309/repositories

### HPC System Login
To login to HPC from your system terminal:
```bash
ssh -p 22 <username>@hpclogin.hpc.ford.com
ssh hpcloginml
```

### HPC Cluster Login
To login to HPC k8s cluster use:
```bash
klogin prod
```

### Automated Deployment Script
The `deploy_to_hpc.sh` script automates the entire deployment process:
1. Transfers files to HPC
2. Builds Docker image 
3. Pushes image to the registry
4. Deploys to your user namespace

To use the deployment script:
```bash
./deploy_to_hpc.sh
```

### Application-Level Namespace
You can also request an application-level namespace instead of using your user namespace. 

Refer to this documentation for requesting an application-level namespace: https://docs.hpc.ford.com/k8s/namespace-app/

Once an application-level namespace is created, the app can be deployed to it instead of a user namespace.

## CaaS Deployment
For CaaS (Container as a Service) deployment, users need to have access to the Ford CaaS platform.

### CaaS Namespace Setup
To get a namespace on CaaS, follow the documentation here: https://docs.ford.com/caas/docs/getting-started/onboarding/get-a-namespace/

The current deployment uses the namespace "cdpr-ocranalyzer".

### CaaS Registry Access
The CaaS registry is available at: https://registry.ford.com/

### Automated Deployment Script
The `deploy_to_caas.sh` script automates the CaaS deployment process:
1. Builds Docker image
2. Pushes image to the CaaS registry
3. Deploys to the specified CaaS namespace

To use the CaaS deployment script:
```bash
./deploy_to_caas.sh
```

**Note:** Ensure you have the necessary permissions and access to the CaaS platform before running the deployment script.

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
