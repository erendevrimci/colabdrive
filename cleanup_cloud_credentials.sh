#!/bin/bash

# Exit on error
set -e

# Function to check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Ask for confirmation
read -p "This will remove all ColabDrive credentials and project. Continue? (y/n): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo "Starting cleanup process..."

# List and delete all existing OAuth 2.0 client IDs
echo "Removing OAuth 2.0 credentials..."
rm -f ~/.config/gcloud/application_default_credentials.json
rm -f client_secrets.json
rm -f ~/.colabdrive/mycreds.txt

# Revoke all credentials
echo "Revoking gcloud credentials..."
gcloud auth revoke --all 2>/dev/null || true

# Get current project and ensure we're authenticated
gcloud auth login --quiet || true
CURRENT_PROJECT=$(gcloud config get-value project)

if [ ! -z "$CURRENT_PROJECT" ] && [ "$CURRENT_PROJECT" != "None" ]; then
    echo "Cleaning up project: $CURRENT_PROJECT"
    
    # Ensure we're authenticated before proceeding
    gcloud auth login --quiet || true
    
    # Disable APIs with error handling
    echo "Disabling APIs..."
    apis=(
        "drive.googleapis.com"
        "iap.googleapis.com"
        "oauth2.googleapis.com"
        "cloudresourcemanager.googleapis.com"
    )

    for api in "${apis[@]}"; do
        echo "Attempting to disable $api..."
        gcloud services disable $api --force 2>/dev/null || true
        sleep 5
    done
    
    # Delete project with retry
    echo "Deleting project: $CURRENT_PROJECT"
    max_retries=3
    retry_count=0
    while [ $retry_count -lt $max_retries ]; do
        if gcloud projects delete $CURRENT_PROJECT --quiet; then
            break
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -eq $max_retries ]; then
                echo "Warning: Failed to delete project after $max_retries attempts"
                break
            fi
            echo "Project deletion failed. Retrying in 10 seconds..."
            sleep 10
        fi
    done
fi

# Clear gcloud config
echo "Clearing gcloud configuration..."
gcloud config unset project

echo "Cleanup complete! You can now run setup_cloud_credentials.sh for a fresh start."
