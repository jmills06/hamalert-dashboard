# Deployment Guide

## Prerequisites

- Google Cloud Project with billing enabled
- GitHub account
- HamAlert account with triggers configured

## Step-by-Step Deployment

### 1. Create GitHub Repository

```bash
# On your local machine
cd hamalert-dashboard
git init
git add .
git commit -m "Initial commit: HamAlert dashboard setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hamalert-dashboard.git
git push -u origin main
```

Or create the repository directly on GitHub and upload the files.

### 2. Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a descriptive name: `HamAlert Cloud Function Access`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
5. Click "Generate token"
6. **IMPORTANT**: Copy the token immediately - you won't see it again!
7. Save it securely (you'll need it in step 4)

### 3. Enable Required Google Cloud APIs

In your Google Cloud Console:

1. Go to "APIs & Services" → "Enable APIs and Services"
2. Search for and enable:
   - Cloud Functions API
   - Cloud Build API
   - Cloud Logging API

### 4. Deploy the Cloud Function

#### Option A: Using Google Cloud Console (Easier)

1. Go to https://console.cloud.google.com/functions
2. Select your project
3. Click "Create Function"
4. Configure:
   - **Environment**: 2nd gen
   - **Function name**: `hamalert-receiver`
   - **Region**: `us-central1` (or your preferred region)
   
5. **Trigger**:
   - **Trigger type**: HTTPS
   - **Authentication**: ✅ Allow unauthenticated invocations
   - Click "SAVE"
   
6. Click "NEXT"

7. **Runtime, build, connections and security settings**:
   - **Runtime**: Python 3.11
   - **Entry point**: `hamalert_webhook`
   
8. **Runtime environment variables**:
   - Click "ADD VARIABLE"
   - Name: `GITHUB_TOKEN`
   - Value: [Your GitHub Personal Access Token from step 2]
   - Click "ADD VARIABLE" again
   - Name: `GITHUB_REPO`
   - Value: `YOUR_USERNAME/hamalert-dashboard` (replace with your actual username)

9. **Source code**:
   - Select "Inline Editor"
   - Replace `main.py` content with the content from `cloud-function/main.py`
   - Replace `requirements.txt` content with the content from `cloud-function/requirements.txt`

10. Click "DEPLOY"

11. Wait for deployment (may take 2-3 minutes)

12. **Copy the Function URL** - You'll see it at the top of the function details page
    - Format: `https://us-central1-YOUR_PROJECT.cloudfunctions.net/hamalert-receiver`

#### Option B: Using gcloud CLI

```bash
cd cloud-function

gcloud functions deploy hamalert-receiver \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=hamalert_webhook \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars=GITHUB_TOKEN=YOUR_TOKEN,GITHUB_REPO=YOUR_USERNAME/hamalert-dashboard
```

Replace `YOUR_TOKEN` and `YOUR_USERNAME` with your actual values.

### 5. Configure HamAlert

1. Log into HamAlert: https://hamalert.org
2. Go to your profile/settings
3. Navigate to "Destinations" section
4. Find "URL notifications" section
5. Configure:
   - **URL**: Your Cloud Function URL from step 4
   - **Method**: POST (or POST (Form) if that's an option)
   - Save the configuration

### 6. Test the Setup

#### Test 1: Manual trigger
If HamAlert has a "test" button, use it to send a test notification.

#### Test 2: Wait for a real spot
Wait for a real spot that matches your HamAlert triggers.

#### Test 3: Verify data collection

1. Check Cloud Function logs:
   - Go to Cloud Functions in GCP Console
   - Click on `hamalert-receiver`
   - Go to "LOGS" tab
   - You should see incoming requests

2. Check GitHub repository:
   - Go to your `hamalert-dashboard` repository
   - Look for `spots.json` file (it will be created after first spot)
   - View the file to see the spot data structure

### 7. Monitor and Debug

**View Cloud Function Logs:**
```bash
gcloud functions logs read hamalert-receiver --region=us-central1 --limit=50
```

**Check GitHub API Rate Limits:**
If you're getting many spots, monitor your GitHub API usage. The free tier allows 5,000 requests per hour.

## Troubleshooting

### "404 Not Found" on spots.json
- Normal! The file won't exist until the first spot is received
- Wait for a spot that matches your HamAlert criteria

### "401 Unauthorized" when updating GitHub
- Check that your GitHub token is correct
- Verify the token has `repo` scope
- Make sure GITHUB_REPO format is correct: `username/repo-name`

### No spots appearing
- Check Cloud Function logs for incoming requests
- Verify HamAlert URL is configured correctly
- Test your HamAlert triggers are working (check if you get mobile notifications)
- Make sure the Cloud Function URL allows unauthenticated invocations

### Function times out
- Check that all required APIs are enabled
- Verify your GitHub token is valid
- Check Cloud Function logs for specific errors

## Next Steps

Once you have spot data in `spots.json`:
1. Review the data structure
2. Design the dashboard layout
3. Create `docs/index.html` with the dashboard
4. Enable GitHub Pages to host the dashboard
5. Configure DakBoard to display your dashboard URL

## Cost Considerations

- **Google Cloud Functions**: Free tier includes 2 million invocations/month
- **GitHub API**: 5,000 requests/hour for authenticated requests
- **GitHub Pages**: Free for public repositories

For typical HamAlert usage (even dozens of spots per day), this should stay within free tiers.
