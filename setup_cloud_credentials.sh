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

# Wait for IAM permissions to propagate
echo "Waiting for permissions to propagate..."
sleep 60

# Enable APIs with retries
enable_api() {
    local api=$1
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        echo "Enabling $api (attempt $((retry_count + 1))/$max_retries)..."
        if gcloud services enable $api; then
            echo "$api enabled successfully"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -eq $max_retries ]; then
                echo "Failed to enable $api after $max_retries attempts"
                return 1
            fi
            echo "Retrying in 30 seconds..."
            sleep 30
        fi
    done
}

# Enable APIs in specific order
apis=(
    "oauth2.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "drive.googleapis.com"
    "iap.googleapis.com"
)

for api in "${apis[@]}"; do
    if ! enable_api $api; then
        echo "Warning: Failed to enable $api"
    fi
    sleep 15  # Wait between APIs
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
