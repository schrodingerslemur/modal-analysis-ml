#!/bin/bash

# Define color codes for better readability
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Load environment variables from script.env
if [ -f script.env ]; then
  export $(grep -v '^#' script.env | xargs)
else
  echo -e "${RED}Environment file script.env not found!${NC}"
  exit 1
fi

# Fetch the current user's username
CURRENT_USER=$(whoami)
echo -e "${BLUE}Current user: ${CURRENT_USER}${NC}"

OC_SERVER="https://api.pp101.caas.gcp.ford.com:6443"
OC_PROJECT="cdpr-ocranalyser"

# Check if the user is already logged in to OpenShift
echo -e "${CYAN}Checking OpenShift login status...${NC}"
if ! oc whoami &>/dev/null; then
    echo -e "${YELLOW}Not logged in to OpenShift. Authentication required.${NC}"
    # Prompt the user for the OpenShift login token
    read -sp "Enter your OpenShift login token: " OC_TOKEN
    echo

    # Log in to OpenShift using the user-provided token
    echo -e "${CYAN}Logging in to OpenShift...${NC}"
    if oc login --token=$OC_TOKEN --server=$OC_SERVER; then
        echo -e "${GREEN}Successfully logged in to OpenShift!${NC}"
    else
        echo -e "${RED}Failed to log in to OpenShift!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Already logged in to OpenShift as $(oc whoami)${NC}"
fi

echo -e "${PURPLE}#############################################################################################################${NC}"
echo -e "${PURPLE}TRANSFERING FILE FROM LOCAL DRIVE TO HPC${NC}"

# Define variables - keeping original modal-analysis structure but adapting for server 2
LOCAL_PROJECT_DIR="."
LOCAL_DOCKERFILE="Dockerfile"
REMOTE_HOST="hpclogin.hpc.ford.com"
REMOTE_PROJECT_DIR="/u/$CURRENT_USER/modal-analysis"
REMOTE_HOME_DIR="/u/$CURRENT_USER"

# Transfer the contents of the local project directory to the remote modal-analysis directory
echo -e "${CYAN}Transfer the contents of the local directory to the remote modal-analysis directory.${NC}"
rsync -av --progress \
  --exclude='.venv/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='*.pyd' \
  --exclude='.git/' \
  --exclude='.DS_Store' \
  --exclude='*.log' \
  --exclude='Dockerfile' \
  --exclude='README.md' \
  --exclude='deploy_to_hpc.sh' \
  --exclude='deploy_to_caas.sh' \
  --exclude='script.env' \
  --exclude='manifest_caas.yaml' \
  --exclude='manifest_hpc.yaml' \
  $LOCAL_PROJECT_DIR/ $CURRENT_USER@$REMOTE_HOST:$REMOTE_PROJECT_DIR/

RSYNC_STATUS=$?

# Transfer the Dockerfile to the remote home directory (outside modal-analysis folder)
echo -e "${CYAN}Transfer the Dockerfile to the remote home directory.${NC}"
scp $LOCAL_DOCKERFILE $CURRENT_USER@$REMOTE_HOST:$REMOTE_HOME_DIR/
SCP_STATUS=$?

# Check if all transfers were successful
if [ $RSYNC_STATUS -eq 0 ] && [ $SCP_STATUS -eq 0 ]; then
  echo -e "${GREEN}File transfer completed successfully.${NC}"
else
  echo -e "${RED}File transfer failed.${NC}"
  exit 1
fi

echo -e "${PURPLE}#############################################################################################################${NC}"
echo -e "${PURPLE}Building image and registering the container${NC}"

# Define the registry and robot account details - USING SERVER 2 CREDENTIALS
REGISTRY_URL="registry.ford.com"
ROBOT_USERNAME="gesautaiml+robot_gesautaiml"
# ROBOT_TOKEN is loaded from script.env (same as server 2)

# SSH into HPC and then into the second server
echo -e "${PURPLE}Connecting to HPC servers and building container...${NC}"
ssh -q -T -p 22 $CURRENT_USER@hpclogin.hpc.ford.com << EOF
    echo -e "${CYAN}Connected to hpclogin. Now connecting to hpcloginml...${NC}"
    ssh -T hpcloginml << 'INNER_EOF'
        # Suppress warning messages
        exec 2>/dev/null

        echo -e "${CYAN}Logging in to container registry...${NC}"
        # Log in to the container registry using the robot account
        if buildah login -u $ROBOT_USERNAME -p $CAAS_ROBOT_TOKEN $REGISTRY_URL; then
            echo -e "${GREEN}Successfully logged in to $REGISTRY_URL as $ROBOT_USERNAME${NC}"
        else
            echo -e "${RED}Failed to log in to container registry!${NC}"
            exit 1
        fi

        # Set proxy environment variables
        echo -e "${CYAN}Setting proxy environment variables...${NC}"
        export HTTP_PROXY=http://internet.ford.com:83
        export HTTPS_PROXY=http://internet.ford.com:83
        export NO_PROXY=localhost,127.0.0.1,19.0.0.0/8,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,169.254/16,ford.com,.ford.com,*.ford.com

        # Clean buildah cache
        echo -e "${CYAN}Cleaning buildah cache...${NC}"
        buildah_clean

        # Build with build arguments for proxy (Dockerfile is in home dir, context is modal-analysis dir)
        # USING SERVER 2 REGISTRY PATH STRUCTURE
        cd /u/$CURRENT_USER
        echo -e "${CYAN}Building container image...${NC}"
        if buildah bud --build-arg "https_proxy=http://internet.ford.com:83" --build-arg "http_proxy=http://internet.ford.com:83" --build-arg "no_proxy=.ford.com" -f Dockerfile -t $REGISTRY_URL/gesautaiml/modal-analysis:modal-analysis-image modal-analysis/; then
            echo -e "${GREEN}Container build successful!${NC}"
        else
            echo -e "${RED}Container build failed!${NC}"
            exit 1
        fi

        echo -e "${CYAN}Pushing container image...${NC}"
        if buildah push $REGISTRY_URL/gesautaiml/modal-analysis:modal-analysis-image; then
            echo -e "${GREEN}Container image pushed successfully!${NC}"
        else
            echo -e "${RED}Failed to push container image!${NC}"
            exit 1
        fi

INNER_EOF
EOF

echo -e "${PURPLE}#############################################################################################################${NC}"
echo -e "${PURPLE}Deploying image into OpenShift Cluster${NC}"

# Switch to the desired project
echo -e "${PURPLE}Switching to OpenShift project $OC_PROJECT...${NC}"
oc project $OC_PROJECT

# Local manifest file (you'll need to create an OpenShift-compatible version)
MANIFEST_FILE="manifest_caas.yaml"

# Delete the existing deployment if it exists
echo -e "${YELLOW}Removing existing deployment if it exists...${NC}"
oc delete deployment modal-analysis --ignore-not-found=true

# Delete the existing service if it exists
oc delete service modal-analysis-service --ignore-not-found=true

# Wait for the pods to be completely deleted
echo -e "${CYAN}Waiting for existing pods to terminate...${NC}"
while oc get pods -l app=modal-analysis 2>/dev/null | grep -q Running; do
  echo -e "${YELLOW}Waiting for existing pods to terminate...${NC}"
  sleep 5
done
echo -e "${GREEN}All old pods terminated.${NC}"

# Apply the deployment manifest
echo -e "${PURPLE}Applying deployment configuration...${NC}"
if oc apply -f $MANIFEST_FILE; then
    echo -e "${GREEN}Deployment configuration applied successfully!${NC}"
else
    echo -e "${RED}Failed to apply deployment configuration!${NC}"
    exit 1
fi

# Verify the deployment status
echo -e "${CYAN}Waiting for deployment to complete...${NC}"
if oc rollout status deployment.apps/modal-analysis -n $OC_PROJECT; then
    echo -e "${GREEN}Deployment completed successfully!${NC}"
else
    echo -e "${RED}Deployment failed or timed out!${NC}"
    exit 1
fi

echo -e "${GREEN}==== All operations completed successfully! ====${NC}"

echo -e "${PURPLE}#############################################################################################################${NC}"
