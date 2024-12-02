#!/bin/bash

# Exit on error but allow for retries
set -e

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Prompt for email
read -p "Enter your email address: " EMAIL

# Validate email format
if [[ ! "$EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    echo "Invalid email format"
    exit 1
fi

# Login to Google Cloud
echo "Logging in to Google Cloud..."
gcloud auth login

# Create new project with retry logic
PROJECT_ID="colabdrive-$(date +%Y%m%d%H%M%S)"
echo "Creating project: ${PROJECT_ID}..."

max_retries=3
retry_count=0
retry_delay=60  # seconds

while [ $retry_count -lt $max_retries ]; do
    if gcloud projects create $PROJECT_ID --name="ColabDrive"; then
        echo "Project created successfully"
        break
    else
        retry_count=$((retry_count + 1))
        if [ $retry_count -eq $max_retries ]; then
            echo "Failed to create project after $max_retries attempts"
            exit 1
        fi
        echo "Project creation failed. Waiting ${retry_delay} seconds before retry $retry_count of $max_retries..."
        sleep $retry_delay
    fi
done

# Set the project as active
echo "Setting active project..."
gcloud config set project $PROJECT_ID

# Grant owner role
echo "Granting owner role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$EMAIL" \
    --role="roles/owner"

# Enable Cloud Resource Manager API first
echo "Enabling Cloud Resource Manager API..."
gcloud services enable cloudresourcemanager.googleapis.com
echo "Waiting for Cloud Resource Manager API to be ready..."
sleep 30

# Enable other required APIs
echo "Enabling remaining APIs..."
apis=(
    "drive.googleapis.com"
    "oauth2.googleapis.com"
    "iap.googleapis.com"
)

for api in "${apis[@]}"; do
    echo "Enabling $api..."
    gcloud services enable $api
    sleep 10  # Wait between enabling each API
done

# Create OAuth consent screen
echo "Creating OAuth consent screen..."
gcloud alpha auth application-default set-oauth-consent \
    --application_title="ColabDrive" \
    --support_email="$EMAIL"

# Create OAuth credentials
echo "Creating OAuth credentials..."
gcloud auth application-default login --no-launch-browser

# Create client ID for desktop application
echo "Creating client ID..."
gcloud auth application-default create-client-id \
    --display_name="ColabDrive" \
    --client-type=desktop

# Download credentials
echo "Downloading credentials..."
gcloud auth application-default print-access-token > client_secrets.json

echo "Setup complete! client_secrets.json has been created."
echo "Project ID: $PROJECT_ID"
