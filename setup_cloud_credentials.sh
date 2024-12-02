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

# Create new project
PROJECT_ID="colabdrive-$(date +%Y%m%d%H%M%S)"
echo "Creating project: ${PROJECT_ID}..."
gcloud projects create $PROJECT_ID --name="ColabDrive" || {
    echo "Failed to create project"
    exit 1
}

# Set the project as active
echo "Setting active project..."
gcloud config set project $PROJECT_ID

# Grant owner role
echo "Granting owner role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$EMAIL" \
    --role="roles/owner"

# Enable required APIs
echo "Enabling required APIs..."
apis=(
    "drive.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "oauth2.googleapis.com"
    "iap.googleapis.com"
)

for api in "${apis[@]}"; do
    echo "Enabling $api..."
    gcloud services enable $api || {
        echo "Failed to enable $api"
        exit 1
    }
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
