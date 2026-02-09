#!/bin/bash
set -e

echo "🚀 Complete App Runner Deployment"

# Load env vars
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# Variables
APP_NAME="farm-ai-assistant"
REGION="us-east-1"
ECR_REPO="${APP_NAME}-repo"
ACCOUNT_ID=$(python3 -c "import boto3; print(boto3.client('sts').get_caller_identity()['Account'])")
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}"

echo "📦 Account: $ACCOUNT_ID"
echo "📦 ECR: $ECR_URI"

# Step 1: Create ECR if needed
echo "1️⃣  Creating ECR repository..."
python3 << EOF
import boto3
ecr = boto3.client('ecr', region_name='$REGION')
try:
    ecr.create_repository(repositoryName='$ECR_REPO')
    print("✅ ECR repository created")
except ecr.exceptions.RepositoryAlreadyExistsException:
    print("✅ ECR repository already exists")
EOF

# Step 2: Login to ECR
echo "2️⃣  Logging into ECR..."
python3 << EOF
import boto3, subprocess
ecr = boto3.client('ecr', region_name='$REGION')
token = ecr.get_authorization_token()
auth = token['authorizationData'][0]
import base64
user, pwd = base64.b64decode(auth['authorizationToken']).decode().split(':')
subprocess.run(f"docker login -u {user} -p {pwd} {auth['proxyEndpoint']}".split())
EOF

# Step 3: Build Docker image
echo "3️⃣  Building Docker image..."
docker build -t ${APP_NAME} .

# Step 4: Tag and push
echo "4️⃣  Pushing to ECR..."
docker tag ${APP_NAME}:latest ${ECR_URI}:latest
docker push ${ECR_URI}:latest

# Step 5: Setup IAM role
echo "5️⃣  Setting up IAM role..."
python3 setup_iam_role.py

# Step 6: Deploy to App Runner
echo "6️⃣  Deploying to App Runner..."
python3 deploy_apprunner.py

echo "✅ Done!"
