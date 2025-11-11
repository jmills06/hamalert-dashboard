# HamAlert Dashboard for K8JKU

Real-time display of HamAlert spots designed for 1920x1080 portrait DakBoard display.

## What This Does

- Receives spot notifications from HamAlert via webhook
- Stores the last 50 spots in a GitHub repository
- Will display spots on a custom dashboard (to be built after we see the data)

## Setup Guide

### Part 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Repository name: `hamalert-dashboard`
3. Make it **Public** (required for GitHub Pages later)
4. **Do NOT** initialize with README
5. Click "Create repository"
6. **Keep this tab open** - you'll need the repository URL

### Part 2: Create GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → [Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Token name: `HamAlert Dashboard`
4. Expiration: 90 days (or longer)
5. Select scopes:
   - ✅ **repo** (all repo checkboxes)
6. Click "Generate token" at the bottom
7. **COPY THE TOKEN IMMEDIATELY** - you cannot see it again!
8. Save it somewhere secure (password manager, notes app, etc.)

### Part 3: Deploy Google Cloud Function

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your existing project from the top dropdown
3. Use the search bar at top and search for "Cloud Functions"
4. Click "CREATE FUNCTION"

#### Configuration:

**Basics:**
- Environment: **2nd gen**
- Function name: `hamalert-receiver`
- Region: **us-central1** (or your preferred region)

**Trigger:**
- Trigger type: **HTTPS**
- Authentication: **Allow unauthenticated invocations** ✅
- Click SAVE

**Runtime, build, connections and security settings** (expand this section):
- Memory: **256 MiB**
- Timeout: **60**
- **Runtime environment variables** - Click "ADD VARIABLE" twice to add these:
  
  Variable 1:
  - Name: `GITHUB_TOKEN`
  - Value: (paste your GitHub Personal Access Token from Part 2)
  
  Variable 2:
  - Name: `GITHUB_REPO`
  - Value: `YOUR_GITHUB_USERNAME/hamalert-dashboard`
    (Replace YOUR_GITHUB_USERNAME with your actual GitHub username)

Click **NEXT**

#### Code:

- Runtime: **Python 3.11**
- Entry point: `hamalert_receiver`
- Source code: **Inline editor**

**Copy the files:**
1. Click on `main.py` in the file list (left side)
2. Delete all the default code
3. Copy and paste the entire contents of the `main.py` file from this repository
4. Click on `requirements.txt`
5. Delete the default content
6. Copy and paste the entire contents of the `requirements.txt` file from this repository

Click **DEPLOY**

Wait 1-2 minutes. You'll see a green checkmark when it's ready.

### Part 4: Get Your Function URL

1. Click on your deployed `hamalert-receiver` function
2. Go to the "TRIGGER" tab
3. Copy the **Trigger URL** (looks like `https://us-central1-yourproject.cloudfunctions.net/hamalert-receiver`)

### Part 5: Test the Function

1. Paste the Trigger URL into your browser
2. You should see: `{"status": "ok", "message": "HamAlert receiver is running", "github_configured": true}`
3. If `github_configured` is **false**, go back and check your environment variables

### Part 6: Configure HamAlert

1. Log in to [HamAlert](https://www.hamalert.org/)
2. Click your username (top right) → **Destinations**
3. Scroll down to **URL notifications**
4. Enter your settings:
   - **URL**: (paste your Cloud Function Trigger URL)
   - **Method**: **GET** (start with this - easier to test)
5. Click **Save**

### Part 7: Test It!

**Option 1: Use the Simulate Feature**
1. Go to HamAlert → **Triggers**
2. Click on any trigger you have set up
3. Click **"Simulate"**
4. This will send a test spot to your function

**Option 2: Wait for a Real Spot**
- Just wait for a spot that matches one of your triggers

### Part 8: Verify It Works

1. Wait about 30 seconds after the spot/simulation
2. Go to your GitHub repository
3. You should see a new file: **spots.json**
4. Click on it to view the data

**If you don't see spots.json:**
- Go to Google Cloud Console → Cloud Functions → hamalert-receiver → LOGS
- Look for errors or "Received spot data" messages
- Check that your GITHUB_TOKEN and GITHUB_REPO variables are correct

### Part 9: Let's Review the Data!

Once you have some spots in `spots.json`, **let me know!** 

We'll look at the data structure together and then I'll build a beautiful dashboard that displays your spots in real-time on your DakBoard.

## Files in This Repository

- `main.py` - The Google Cloud Function code (Python)
- `requirements.txt` - Python dependencies for the Cloud Function
- `README.md` - This file
- `spots.json` - Will be auto-created when spots arrive

## Troubleshooting

### The function deployed but nothing happens

**Check the logs:**
1. Cloud Functions → hamalert-receiver → LOGS tab
2. Trigger a test spot from HamAlert
3. Look for "Received spot data" in the logs
4. If you see errors, read the error message carefully

**Common issues:**
- `GITHUB_TOKEN` is incorrect or expired
- `GITHUB_REPO` format is wrong (should be `username/repo-name`, not a URL)
- GitHub token doesn't have the `repo` scope checked

### How to test manually

You can test the endpoint with a web browser or curl:

```
https://YOUR-FUNCTION-URL?callsign=W1AW&frequency=14.250&mode=CW&band=20m
```

Just replace YOUR-FUNCTION-URL with your actual function URL. If it works, you'll see a new entry in spots.json on GitHub.

### GitHub token expired

If your token expires, generate a new one following Part 2 again, then:
1. Go to Cloud Functions → hamalert-receiver
2. Click EDIT
3. Update the GITHUB_TOKEN environment variable
4. Click DEPLOY

## What's Next?

After we collect some sample data:
1. Review the spot data structure
2. Design the dashboard layout
3. Build the HTML dashboard
4. Enable GitHub Pages
5. Add the dashboard URL to your DakBoard
6. Enjoy real-time spots!

## Questions?

If something isn't working:
1. Check Cloud Function logs first (this will tell you what's happening)
2. Verify the environment variables are exactly correct
3. Make sure the GitHub token hasn't expired
4. Test with the manual URL method above to isolate the problem
