# Digital Ocean Spaces Setup Guide

## Step 1: Create a Space

1. Log into your Digital Ocean account
2. Go to **Spaces** in the left menu
3. Click "Create Space"
4. Choose settings:
   - **Region**: NYC3 (or closest to you)
   - **Space Name**: `zonuko-media`
   - **Enable CDN**: YES (makes videos load fast worldwide)
   - **File Listing**: Restricted
5. Click "Create Space"

## Step 2: Generate API Keys

1. Click your profile → **API**
2. Scroll to "Spaces Access Keys"
3. Click "Generate New Key"
4. **Name it**: "Zonuko App"
5. **Copy both keys** (you only see the secret once!)
   - Access Key: Like a username
   - Secret Key: Like a password

## Step 3: Configure Your Local Environment

1. Open `.env` file (create if it doesn't exist)
2. Add these lines:

```
SPACES_ACCESS_KEY=your-access-key-here
SPACES_SECRET_KEY=your-secret-key-here
SPACES_BUCKET_NAME=zonuko-media
SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
```

3. Replace `your-access-key-here` and `your-secret-key-here` with your actual keys
4. Save the file

## Step 4: Test It!

1. Restart your Django server
2. Go to admin: http://127.0.0.1:8000/admin/
3. Click "Projects" → "Add Project"
4. Upload a small test video
5. Save

The video will upload to Digital Ocean Spaces automatically! 🚀

## Pricing

- **Storage**: $5/month for 250GB
- **Transfer**: $0.01/GB (first 1TB free usually)
- **For 5min videos**: ~100MB each, so 250GB = 2500 videos!

## Note

Videos uploaded locally (while testing) will be stored in your project folder.
Once you deploy to production and add Spaces keys, they'll go to Digital Ocean automatically.
