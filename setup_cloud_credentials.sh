#!/bin/bash

# Exit on error but allow for retries
set -e

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check for existing setup
CURRENT_PROJECT=$(gcloud config get-value project)

# Email validation function
validate_email() {
    local email="$1"
    if [[ ! "$email" =~ ^[[:alnum:]._%+-]+@[[:alnum:].-]+\.[[:alpha:]]{2,}$ ]]; then
        return 1
    fi
    return 0
}

# Get and validate email with retry
while true; do
    echo "Please enter your email address (or Ctrl+C to exit):"
    read -r EMAIL
    
    # Remove any whitespace
    EMAIL=$(echo "$EMAIL" | tr -d '[:space:]')
    
    if validate_email "$EMAIL"; then
        echo "Email format validated: $EMAIL"
        break
    else
        echo "Invalid email format. Please enter a valid email address."
        echo "Example: username@domain.com"
    fi
done

if [ ! -z "$CURRENT_PROJECT" ] && [ "$CURRENT_PROJECT" != "None" ]; then
    read -p "Existing project found ($CURRENT_PROJECT). Do you want to use it? (y/n): " USE_EXISTING
    if [[ $USE_EXISTING =~ ^[Yy]$ ]]; then
        PROJECT_ID=$CURRENT_PROJECT
        echo "Using existing project: $PROJECT_ID"
    fi
fi

# Login to Google Cloud
echo "Logging in to Google Cloud..."
gcloud auth login

if [ -z "$PROJECT_ID" ]; then
    # Create new project only if not using existing
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
fi

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
gcloud services enable servicemanagement.googleapis.com --quiet || true
sleep 30

# Verify core services are enabled
echo "Verifying core services..."
if ! gcloud services list --enabled | grep -q "serviceusage.googleapis.com"; then
    echo "Error: Failed to enable core services"
    exit 1
fi

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
    "serviceusage.googleapis.com"
    "iam.googleapis.com"
    "servicemanagement.googleapis.com"
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
gcloud auth application-default login --no-launch-browser \
    --redirect-uri=http://127.0.0.1:8080/

# Configure OAuth consent screen
echo "Configuring OAuth consent screen..."
gcloud services enable iap.googleapis.com
gcloud iap oauth-brand add \
    --application_title="ColabDrive" \
    --support_email="$EMAIL"

# Add authorized redirect URI
echo "Adding authorized redirect URI..."
gcloud iap oauth-client add \
    --display_name="ColabDrive Local" \
    --redirect_uris="http://127.0.0.1:8080/"

# Ensure credentials directory exists
mkdir -p ~/.config/gcloud

# Validate and create client secrets file
echo "Creating client secrets file..."
if [ -f ~/.config/gcloud/application_default_credentials.json ]; then
    # Validate JSON format
    if python3 -c "import json; json.load(open('~/.config/gcloud/application_default_credentials.json'));" 2>/dev/null; then
        cp ~/.config/gcloud/application_default_credentials.json client_secrets.json
        echo "Credentials setup complete!"
    else
        echo "Regenerating credentials file..."
        rm -f ~/.config/gcloud/application_default_credentials.json
        gcloud auth application-default login --no-launch-browser
        cp ~/.config/gcloud/application_default_credentials.json client_secrets.json
    fi
else
    echo "No credentials file found, creating new one..."
    gcloud auth application-default login --no-launch-browser
    cp ~/.config/gcloud/application_default_credentials.json client_secrets.json
fi

# Final validation and setup
if [ ! -s client_secrets.json ]; then
    echo "Error: Failed to create valid credentials file"
    exit 1
fi

# Create .colabdrive config directory
mkdir -p ~/.colabdrive

# Copy credentials to .colabdrive
cp client_secrets.json ~/.colabdrive/
echo "Project ID: $PROJECT_ID" > ~/.colabdrive/project_info.txt

echo "Setup complete! Credentials saved to:"
echo "1. ./client_secrets.json"
echo "2. ~/.colabdrive/client_secrets.json"
echo "3. ~/.config/gcloud/application_default_credentials.json"
echo "Project ID: $PROJECT_ID"

echo "Setup complete! client_secrets.json has been created."
echo "Project ID: $PROJECT_ID"
