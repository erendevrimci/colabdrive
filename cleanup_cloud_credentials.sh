#!/bin/bash

# Exit on error
set -e

# Function to check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI is not installed. Please install it first."
    exit 1
fi

echo "Starting cleanup process..."

# List and delete all existing OAuth 2.0 client IDs
echo "Removing OAuth 2.0 credentials..."
rm -f ~/.config/gcloud/application_default_credentials.json
rm -f client_secrets.json
rm -f ~/.colabdrive/mycreds.txt

# Revoke all credentials
echo "Revoking gcloud credentials..."
gcloud auth revoke --all

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project)

if [ ! -z "$CURRENT_PROJECT" ]; then
    echo "Cleaning up project: $CURRENT_PROJECT"
    
    # Disable APIs
    echo "Disabling APIs..."
    gcloud services disable drive.googleapis.com --force
    gcloud services disable cloudresourcemanager.googleapis.com --force
    gcloud services disable oauth2.googleapis.com --force
    gcloud services disable iap.googleapis.com --force
    
    # Delete project
    echo "Deleting project: $CURRENT_PROJECT"
    gcloud projects delete $CURRENT_PROJECT --quiet
fi

# Clear gcloud config
echo "Clearing gcloud configuration..."
gcloud config unset project

echo "Cleanup complete! You can now run setup_cloud_credentials.sh for a fresh start."
