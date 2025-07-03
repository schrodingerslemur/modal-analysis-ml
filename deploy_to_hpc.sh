#!/bin/bash

# Load environment variables from script.env
if [ -f script.env ]; then
  export $(grep -v '^#' script.env | xargs)
else
  echo "Environment file script.env not found!"
  exit 1
fi

echo "#############################################################################################################"
echo "TRANSFERING FILE FROM LOCAL DRIVE TO HPC"

# Fetch the current user's username
CURRENT_USER=$(whoami)

# Define variables
LOCAL_PROJECT_DIR="."
LOCAL_DOCKERFILE="Dockerfile"
REMOTE_HOST="hpclogin.hpc.ford.com"
REMOTE_PROJECT_DIR="/u/$CURRENT_USER/modal-analysis"
REMOTE_HOME_DIR="/u/$CURRENT_USER"

# Transfer the contents of the local project directory to the remote modal-analysis directory
echo "Transfer the contents of the local directory to the remote modal-analysis directory."
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
  --exclude='script.env' \
  --exclude='manifest.yaml' \
  $LOCAL_PROJECT_DIR/ $CURRENT_USER@$REMOTE_HOST:$REMOTE_PROJECT_DIR/

RSYNC_STATUS=$?

# Transfer the Dockerfile to the remote home directory (outside modal-analysis folder)
echo "Transfer the Dockerfile to the remote home directory."
scp $LOCAL_DOCKERFILE $CURRENT_USER@$REMOTE_HOST:$REMOTE_HOME_DIR/
SCP_STATUS=$?

# Check if all transfers were successful
if [ $RSYNC_STATUS -eq 0 ] && [ $SCP_STATUS -eq 0 ]; then
  echo "File transfer completed successfully."
else
  echo "File transfer failed."
  exit 1
fi

echo "#############################################################################################################"
echo "Building image and registering the container"

# Define the registry and robot account details
REGISTRY_URL="harbor.hpc.ford.com"
ROBOT_USERNAME="robot\\\$modal-analysis+robot-modal-analysis"

# SSH into HPC and then into the second server
ssh -q -t -p 22 $CURRENT_USER@hpclogin.hpc.ford.com << EOF
    ssh -t hpcloginml << 'INNER_EOF'
        # Suppress warning messages
        exec 2>/dev/null

        # Log in to the container registry using the robot account
        echo "Logging in using --- buildah login -u $ROBOT_USERNAME -p $ROBOT_TOKEN $REGISTRY_URL"
        buildah login -u $ROBOT_USERNAME -p $ROBOT_TOKEN $REGISTRY_URL
        echo "Logged in to $REGISTRY_URL as $ROBOT_USERNAME"

        # Set proxy environment variables
        export HTTP_PROXY=http://internet.ford.com:83
        export HTTPS_PROXY=http://internet.ford.com:83
        export NO_PROXY=localhost,127.0.0.1,19.0.0.0/8,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,169.254/16,ford.com,.ford.com,*.ford.com

        # Clean buildah cache
        buildah_clean

        # Build with build arguments for proxy (Dockerfile is in home dir, context is modal-analysis dir)
        cd /u/$CURRENT_USER
        buildah bud --build-arg "https_proxy=http://internet.ford.com:83" --build-arg "http_proxy=http://internet.ford.com:83" --build-arg "no_proxy=.ford.com" -f Dockerfile -t $REGISTRY_URL/modal-analysis/modal-analysis-image:v1 modal-analysis/
        buildah push $REGISTRY_URL/modal-analysis/modal-analysis-image:v1

    INNER_EOF
EOF

echo "#############################################################################################################"
echo "Deploying image into HPC Kubernetes Cluster"

NAMESPACE="$CURRENT_USER"
# Local manifest file
MANIFEST_FILE="manifest.yaml"

# Prompt the user for the login details
echo "Enter your login details:"
klogin prod

# Delete the existing deployment if it exists
kubectl delete deployment modal-analysis -n $NAMESPACE --ignore-not-found=true

# Delete the existing service if it exists
kubectl delete service modal-analysis-service -n $NAMESPACE --ignore-not-found=true

# Wait for the pods to be completely deleted
echo "Waiting for existing pods to terminate..."
while kubectl get pods -l app=modal-analysis -n $NAMESPACE 2>/dev/null | grep -q Running; do
  echo "Waiting for existing pods to terminate..."
  sleep 5
done

# Apply the deployment manifest
echo "Applying deployment manifest..."
kubectl apply -f $MANIFEST_FILE -n $NAMESPACE

# Verify the deployment status
echo "Checking deployment status..."
kubectl rollout status deployment.apps/modal-analysis -n $NAMESPACE

echo "Deployment completed successfully."

echo "#############################################################################################################"
