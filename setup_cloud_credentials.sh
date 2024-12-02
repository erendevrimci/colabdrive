#!/bin/bash

# Exit on error but allow for retries
set -e

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Function to check if project exists
check_project_exists() {
    local project_id=$1
    gcloud projects list --filter="project_id:$project_id" --format="value(project_id)" | grep -q "^$project_id$"
    return $?
}

# Function to create project with retry
create_project() {
    local project_id=$1
    local max_attempts=3
    local attempt=1
    local wait_time=60

    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt to create project ${project_id}..."
        
        if check_project_exists "$project_id"; then
            echo "Project $project_id already exists."
            return 0
        fi

        if gcloud projects create $project_id --name="ColabDrive Test" 2>/dev/null; then
            echo "Project created successfully!"
            return 0
        else
            if [ $attempt -lt $max_attempts ]; then
                echo "Failed to create project. Waiting ${wait_time} seconds before retry..."
                sleep $wait_time
                wait_time=$((wait_time * 2))
            fi
        fi
        attempt=$((attempt + 1))
    done
    
    echo "Failed to create project after $max_attempts attempts."
    return 1
}

# Prompt for email
read -p "Enter your email address: " EMAIL

# Login to Google Cloud
echo "Logging in to Google Cloud..."
gcloud auth login

# Create new project with retry logic
PROJECT_ID="colabdrive-test-$(date +%Y%m%d)"
echo "Setting up project ${PROJECT_ID}..."
create_project $PROJECT_ID || exit 1

# Set the project as active
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling Google Drive API..."
gcloud services enable drive.googleapis.com

# Set quota project
echo "Setting quota project..."
gcloud auth application-default set-quota-project $PROJECT_ID

# Configure OAuth consent screen
echo "Configuring OAuth consent screen..."
gcloud iap oauth-brands create \
    --application_title="ColabDrive Test" \
    --support_email="$EMAIL"

# Create OAuth client ID and download credentials
echo "Creating OAuth client ID..."
gcloud auth application-default login --client-id-file=client_secrets.json

echo "Downloading OAuth 2.0 Client ID..."
gcloud auth application-default print-access-token > client_secrets.json

echo "Setup complete! client_secrets.json has been created."
