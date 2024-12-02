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

# Enable core APIs first
echo "Enabling core APIs..."
gcloud services enable serviceusage.googleapis.com --quiet || true
sleep 30

# Enable APIs with retries
enable_api() {
    local api=$1
    local max_retries=3
    local retry_count=0
    local retry_delay=45
    
    while [ $retry_count -lt $max_retries ]; do
        echo "Enabling $api (attempt $((retry_count + 1))/$max_retries)..."
        if gcloud services enable $api --async; then
            echo "Initiated enabling $api"
            sleep $retry_delay  # Wait for async operation
            if gcloud services list --enabled --filter="name:$api" | grep -q "$api"; then
                echo "$api enabled successfully"
                return 0
            fi
        fi
        retry_count=$((retry_count + 1))
        if [ $retry_count -eq $max_retries ]; then
            echo "Warning: Issues enabling $api after $max_retries attempts"
            return 1
        fi
        echo "Retrying in $retry_delay seconds..."
        sleep $retry_delay
    done
}

# Enable APIs in specific order
apis=(
    "cloudresourcemanager.googleapis.com"
    "oauth2.googleapis.com"
    "drive.googleapis.com"
    "iap.googleapis.com"
)

for api in "${apis[@]}"; do
    if ! enable_api $api; then
        echo "Warning: Failed to enable $api"
    fi
    sleep 15  # Wait between APIs
done

# Create OAuth credentials
echo "Creating OAuth credentials..."
gcloud auth application-default login

# Ensure credentials directory exists
mkdir -p ~/.config/gcloud

# Create client secrets file
echo "Creating client secrets file..."
if [ -f ~/.config/gcloud/application_default_credentials.json ]; then
    cp ~/.config/gcloud/application_default_credentials.json client_secrets.json
    echo "Credentials setup complete!"
else
    echo "Error: Failed to create credentials file"
    exit 1
fi

echo "Setup complete! client_secrets.json has been created."
echo "Project ID: $PROJECT_ID"
