# Getting Started with Google Cloud Credentials

This guide will walk you through the process of obtaining Google Cloud credentials for using ColabDrive.

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project dropdown at the top of the page
4. Click "New Project"
5. Enter a project name (e.g., "ColabDrive")
6. Click "Create"

## Step 2: Enable the Google Drive API

1. In the Cloud Console, go to the [API Library](https://console.cloud.google.com/apis/library)
2. Search for "Google Drive API"
3. Click on "Google Drive API"
4. Click "Enable"

## Step 3: Create Credentials

1. Go to the [Credentials page](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials"
3. Select "OAuth client ID"
4. If this is your first time, you'll need to configure the OAuth consent screen:
   - Click "Configure Consent Screen"
   - Choose "External" user type
   - Fill in the required information (app name, user support email, developer contact)
   - For scopes, add Google Drive API scopes
   - Add your email as a test user
   - Save and continue

5. Back on the credentials page:
   - Choose "Desktop app" as the application type
   - Give it a name (e.g., "ColabDrive Client")
   - Click "Create"

## Step 4: Download and Use Credentials

1. After creating the credentials, you'll see a download button (looks like a download icon)
2. Click download to get your `client_secrets.json` file
3. Replace the placeholder content in your `client_secrets.json` with the downloaded content

## Step 5: Set Up in ColabDrive

1. Place the `client_secrets.json` file in your project root directory
2. The first time you run ColabDrive, it will use these credentials to authenticate
3. You'll be prompted to authorize the application in your browser
4. After authorization, credentials will be saved for future use

## Important Notes

- Keep your `client_secrets.json` file secure and never commit it to public repositories
- If you're using Google Colab, you'll need to upload the credentials file each time you start a new session
- For testing, you can use the credentials immediately
- For production use, you'll need to verify your app through Google's OAuth verification process

## Troubleshooting

If you encounter authentication errors:
1. Ensure the Google Drive API is enabled
2. Check that your credentials are properly configured
3. Verify you've added yourself as a test user in the OAuth consent screen
4. Make sure the `client_secrets.json` file is in the correct location

For additional help, refer to the [Google Cloud Documentation](https://cloud.google.com/docs) or open an issue in our repository.
