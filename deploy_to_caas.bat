@echo off
setlocal enabledelayedexpansion

REM Define color codes for better readability (Windows doesn't support ANSI colors in standard cmd)
REM We'll use echo statements without colors, or you can install a color utility

echo Loading environment variables from script.env...
if not exist script.env (
    echo ERROR: Environment file script.env not found!
    exit /b 1
)

REM Load environment variables from script.env
for /f "usebackq tokens=1,2 delims==" %%a in ("script.env") do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        set %%a=%%b
    )
)

REM Fetch the current user's username
set CURRENT_USER=%USERNAME%
echo Current user: %CURRENT_USER%

set OC_SERVER=https://api.pp101.caas.gcp.ford.com:6443
set OC_PROJECT=cdpr-ocranalyser

REM Check if the user is already logged in to OpenShift
echo Checking OpenShift login status...
oc whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo Not logged in to OpenShift. Authentication required.
    set /p OC_TOKEN="Enter your OpenShift login token: "
    
    echo Logging in to OpenShift...
    oc login --token=!OC_TOKEN! --server=%OC_SERVER%
    if %errorlevel% neq 0 (
        echo Failed to log in to OpenShift!
        exit /b 1
    )
    echo Successfully logged in to OpenShift!
) else (
    for /f %%i in ('oc whoami') do set OC_USER=%%i
    echo Already logged in to OpenShift as !OC_USER!
)

echo #############################################################################################################
echo TRANSFERING FILE FROM LOCAL DRIVE TO HPC

REM Define variables
set LOCAL_PROJECT_DIR=.
set LOCAL_DOCKERFILE=Dockerfile
set REMOTE_HOST=hpclogin.hpc.ford.com
set REMOTE_PROJECT_DIR=/u/%CURRENT_USER%/modal-analysis
set REMOTE_HOME_DIR=/u/%CURRENT_USER%

REM Transfer files using rsync (requires rsync for Windows or WSL)
echo Transfer the contents of the local directory to the remote modal-analysis directory.
rsync -av --progress ^
  --exclude=.venv/ ^
  --exclude=__pycache__/ ^
  --exclude=*.pyc ^
  --exclude=*.pyo ^
  --exclude=*.pyd ^
  --exclude=.git/ ^
  --exclude=.DS_Store ^
  --exclude=*.log ^
  --exclude=Dockerfile ^
  --exclude=README.md ^
  --exclude=deploy_to_hpc.sh ^
  --exclude=deploy_to_caas.sh ^
  --exclude=script.env ^
  --exclude=manifest_caas.yaml ^
  --exclude=manifest_hpc.yaml ^
  %LOCAL_PROJECT_DIR%/ %CURRENT_USER%@%REMOTE_HOST%:%REMOTE_PROJECT_DIR%/

set RSYNC_STATUS=%errorlevel%

REM Transfer the Dockerfile to the remote home directory
echo Transfer the Dockerfile to the remote home directory.
scp %LOCAL_DOCKERFILE% %CURRENT_USER%@%REMOTE_HOST%:%REMOTE_HOME_DIR%/
set SCP_STATUS=%errorlevel%

REM Check if all transfers were successful
if %RSYNC_STATUS% equ 0 if %SCP_STATUS% equ 0 (
    echo File transfer completed successfully.
) else (
    echo File transfer failed.
    exit /b 1
)

echo #############################################################################################################
echo Building image and registering the container

REM Define the registry and robot account details
set REGISTRY_URL=registry.ford.com
set HPC_REGISTRY_URL=harbor.hpc.ford.com
set ROBOT_USERNAME=gesautaiml+robot_gesautaiml
set HPC_ROBOT_USERNAME=robot\\\$modal-analysis+robot-modal-analysis

echo Connecting to HPC servers and building container...

REM Create a temporary script file for SSH commands
echo echo Connected to hpclogin. Now connecting to hpcloginml... > temp_ssh_commands.sh
echo ssh -T hpcloginml ^<^< 'INNER_EOF' >> temp_ssh_commands.sh
echo echo Logging in to container registry... >> temp_ssh_commands.sh
echo if buildah login -u %ROBOT_USERNAME% -p %CAAS_ROBOT_TOKEN% %REGISTRY_URL%; then >> temp_ssh_commands.sh
echo     echo Successfully logged in to %REGISTRY_URL% as %ROBOT_USERNAME% >> temp_ssh_commands.sh
echo else >> temp_ssh_commands.sh
echo     echo Failed to log in to container registry! >> temp_ssh_commands.sh
echo     exit 1 >> temp_ssh_commands.sh
echo fi >> temp_ssh_commands.sh
echo buildah login -u %HPC_ROBOT_USERNAME% -p %ROBOT_TOKEN% %HPC_REGISTRY_URL% >> temp_ssh_commands.sh
echo echo Setting proxy environment variables... >> temp_ssh_commands.sh
echo export HTTP_PROXY=http://internet.ford.com:83 >> temp_ssh_commands.sh
echo export HTTPS_PROXY=http://internet.ford.com:83 >> temp_ssh_commands.sh
echo export NO_PROXY=localhost,127.0.0.1,19.0.0.0/8,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,169.254/16,ford.com,.ford.com,*.ford.com >> temp_ssh_commands.sh
echo echo Cleaning buildah cache... >> temp_ssh_commands.sh
echo buildah_clean >> temp_ssh_commands.sh
echo cd /u/%CURRENT_USER% >> temp_ssh_commands.sh
echo echo Building container image... >> temp_ssh_commands.sh
echo if buildah bud --build-arg "https_proxy=http://internet.ford.com:83" --build-arg "http_proxy=http://internet.ford.com:83" --build-arg "no_proxy=.ford.com" -f Dockerfile -t %REGISTRY_URL%/gesautaiml/modal-analysis:modal-analysis-image modal-analysis/; then >> temp_ssh_commands.sh
echo     echo Container build successful! >> temp_ssh_commands.sh
echo else >> temp_ssh_commands.sh
echo     echo Container build failed! >> temp_ssh_commands.sh
echo     exit 1 >> temp_ssh_commands.sh
echo fi >> temp_ssh_commands.sh
echo echo Pushing container image... >> temp_ssh_commands.sh
echo if buildah push %REGISTRY_URL%/gesautaiml/modal-analysis:modal-analysis-image; then >> temp_ssh_commands.sh
echo     echo Container image pushed successfully! >> temp_ssh_commands.sh
echo else >> temp_ssh_commands.sh
echo     echo Failed to push container image! >> temp_ssh_commands.sh
echo     exit 1 >> temp_ssh_commands.sh
echo fi >> temp_ssh_commands.sh
echo INNER_EOF >> temp_ssh_commands.sh

REM Execute SSH commands
ssh -q -T -p 22 %CURRENT_USER%@hpclogin.hpc.ford.com < temp_ssh_commands.sh

REM Clean up temporary file
del temp_ssh_commands.sh

echo #############################################################################################################
echo Deploying image into OpenShift Cluster

REM Switch to the desired project
echo Switching to OpenShift project %OC_PROJECT%...
oc project %OC_PROJECT%

REM Local manifest file
set MANIFEST_FILE=manifest_caas.yaml

REM Delete the existing deployment if it exists
echo Removing existing deployment if it exists...
oc delete deployment modal-analysis --ignore-not-found=true

REM Delete the existing service if it exists
oc delete service modal-analysis-service --ignore-not-found=true

REM Wait for the pods to be completely deleted
echo Waiting for existing pods to terminate...
:wait_loop
oc get pods -l app=modal-analysis 2>nul | findstr Running >nul 2>&1
if %errorlevel% equ 0 (
    echo Waiting for existing pods to terminate...
    timeout /t 5 /nobreak >nul
    goto wait_loop
)
echo All old pods terminated.

REM Apply the deployment manifest
echo Applying deployment configuration...
oc apply -f %MANIFEST_FILE%
if %errorlevel% neq 0 (
    echo Failed to apply deployment configuration!
    exit /b 1
)
echo Deployment configuration applied successfully!

REM Verify the deployment status
echo Waiting for deployment to complete...
oc rollout status deployment.apps/modal-analysis -n %OC_PROJECT%
if %errorlevel% neq 0 (
    echo Deployment failed or timed out!
    exit /b 1
)
echo Deployment completed successfully!

echo ==== All operations completed successfully! ====

echo #############################################################################################################

pause
