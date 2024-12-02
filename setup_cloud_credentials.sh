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
