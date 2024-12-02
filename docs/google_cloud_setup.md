# Setting Up Google Cloud Credentials Using gcloud CLI

This guide shows how to set up Google Cloud credentials for ColabDrive using the command line.

## Prerequisites

1. Install the Google Cloud SDK:
   ```bash
   # For macOS with Homebrew
   brew install google-cloud-sdk
   ```

## Step 1: Initialize gcloud and Create Project

```bash
# Login to Google Cloud
gcloud auth login

# Create new project
gcloud projects create colabdrive-test --name="ColabDrive Test"

# Set the project as active
gcloud config set project colabdrive-test
```

## Step 2: Enable Required APIs

```bash
# Enable the Google Drive API
gcloud services enable drive.googleapis.com
```

## Step 3: Configure OAuth Consent Screen

```bash
# Create OAuth consent screen configuration
gcloud alpha iap oauth-brand create \
    --application_title="ColabDrive Test" \
    --support_email="your-email@example.com"

# Add test users (for testing mode)
gcloud alpha iap oauth-clients add-iam-policy-binding \
    --role=roles/iap.httpsResourceAccessor \
    --member=user:your-email@example.com
```

## Step 4: Create OAuth Client ID

```bash
# Create OAuth client ID for desktop application
gcloud alpha iap oauth-clients create \
    --display_name="ColabDrive Test Client" \
    --type=desktop

# Download the credentials
gcloud alpha iap oauth-clients get-credentials \
    --client_id=YOUR_CLIENT_ID \
    --output-file=client_secrets.json
```

## Step 5: Set Up in ColabDrive

1. The downloaded `client_secrets.json` will be automatically placed in your project directory
2. First run will prompt for authorization in your browser
3. Credentials will be saved for future use

## Important Notes

- Keep `client_secrets.json` secure and never commit it to public repositories
- For Colab usage, upload credentials each new session
- Only test users can access the app in testing mode
- For production, complete Google's OAuth verification process

## Troubleshooting

Run these commands to verify your setup:
```bash
# Check API status
gcloud services list --enabled

# Verify OAuth configuration
gcloud alpha iap oauth-brands list
gcloud alpha iap oauth-clients list

# Check project settings
gcloud config list
```

For more help:
```bash
gcloud help
```
