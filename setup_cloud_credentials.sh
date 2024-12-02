#!/bin/bash

# Exit on error
set -e

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Prompt for email
read -p "Enter your email address: " EMAIL

# Login to Google Cloud
echo "Logging in to Google Cloud..."
gcloud auth login

# Create new project
PROJECT_ID="colabdrive-test-$(date +%Y%m%d)"
echo "Creating project ${PROJECT_ID}..."
gcloud projects create $PROJECT_ID --name="ColabDrive Test"

# Set the project as active
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling Google Drive API..."
gcloud services enable drive.googleapis.com

# Configure OAuth consent screen
echo "Configuring OAuth consent screen..."
gcloud alpha iap oauth-brand create \
    --application_title="ColabDrive Test" \
    --support_email="$EMAIL"

# Add test user
echo "Adding test user..."
gcloud alpha iap oauth-clients add-iam-policy-binding \
    --role=roles/iap.httpsResourceAccessor \
    --member="user:$EMAIL"

# Create OAuth client ID
echo "Creating OAuth client ID..."
CLIENT_INFO=$(gcloud alpha iap oauth-clients create \
    --display_name="ColabDrive Test Client" \
    --type=desktop)

# Extract client ID
CLIENT_ID=$(echo $CLIENT_INFO | grep -o 'client_id: [^ ]*' | cut -d' ' -f2)

# Download credentials
echo "Downloading credentials..."
gcloud alpha iap oauth-clients get-credentials \
    --client_id=$CLIENT_ID \
    --output-file=client_secrets.json

echo "Setup complete! client_secrets.json has been created."
