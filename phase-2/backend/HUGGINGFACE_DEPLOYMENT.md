# Hugging Face Spaces Deployment Guide

## Step 1: Create Hugging Face Account
1. Go to https://huggingface.co/join
2. Sign up (no card required!)
3. Verify your email

## Step 2: Create a New Space

1. Go to https://huggingface.co/new-space
2. Fill in the details:
   - **Space name**: `hackathon-todo-backend`
   - **License**: MIT
   - **Select SDK**: Docker
   - **Space hardware**: CPU basic (free)
   - **Visibility**: Public (or Private if you prefer)

3. Click **"Create Space"**

## Step 3: Add Files to Space

You have two options:

### Option A: Upload via Web Interface (Easier)

1. In your new Space, click **"Files"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload these files from `phase-2/backend/`:
   - `Dockerfile`
   - `requirements.txt`
   - `main.py`
   - `config.py`
   - `database.py`
   - `models.py`
   - `middleware.py`
   - All folders: `auth/`, `routes/`, `utils/`, `api/`
   - `README.md` (the one with YAML frontmatter)

### Option B: Git Push (Advanced)

```bash
# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/hackathon-todo-backend
cd hackathon-todo-backend

# Copy backend files
cp -r /path/to/phase-2/backend/* .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

## Step 4: Configure Environment Variables (Secrets)

1. In your Space, go to **"Settings"** tab
2. Scroll to **"Repository secrets"**
3. Add these secrets:

```
DATABASE_URL = your_neon_database_url_here

JWT_SECRET = your_jwt_secret_here

ENVIRONMENT = production

CORS_ORIGINS = https://your-frontend-url.vercel.app

GROQ_API_KEY = your_groq_api_key_here

GEMINI_API_KEY = your_gemini_api_key_here (optional)
```

**Important**: Click **"Add secret"** for each one.

## Step 5: Wait for Build

1. Hugging Face will automatically build your Docker container
2. Check the **"Logs"** tab to monitor progress
3. Build takes 2-5 minutes
4. Once complete, your Space will show "Running"

## Step 6: Get Your API URL

Your backend will be available at:
```
https://YOUR_USERNAME-hackathon-todo-backend.hf.space
```

For example:
```
https://laibajawed-hackathon-todo-backend.hf.space
```

## Step 7: Initialize Database

1. Go to your Space
2. Click **"Logs"** tab
3. You may need to run init_db.py manually via the Space's terminal (if available)

Or connect via API and let the first request create tables (if you add init logic to startup).

## Step 8: Update Frontend

Update your frontend `.env.local`:
```
NEXT_PUBLIC_API_URL=https://YOUR_USERNAME-hackathon-todo-backend.hf.space
```

Also update backend CORS:
```
CORS_ORIGINS=https://frontend-eta-beige-65.vercel.app,https://YOUR_USERNAME-hackathon-todo-backend.hf.space
```

## Step 9: Test Your API

Visit:
```
https://YOUR_USERNAME-hackathon-todo-backend.hf.space/docs
```

You should see FastAPI Swagger documentation.

## Important Notes

### Free Tier Benefits
- ✅ No card required
- ✅ Always-on (no cold starts)
- ✅ Automatic HTTPS
- ✅ Good for demos and small projects

### Limitations
- CPU only (no GPU on free tier)
- Limited compute resources
- Public by default (can make private)

### Auto-Deploy
Hugging Face automatically rebuilds when you push to the Space's git repo.

### Monitoring
- View logs in real-time
- Check build status
- Monitor resource usage

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify all files are uploaded
- Check logs for specific errors

### Port Issues
- Hugging Face expects port 7860
- Make sure Dockerfile exposes 7860
- Start command should use `--port 7860`

### Environment Variables Not Working
- Secrets must be added in Settings → Repository secrets
- Restart the Space after adding secrets
- Check logs to see if variables are loaded

### Database Connection Issues
- Verify DATABASE_URL is correct
- Ensure Neon database allows connections from Hugging Face IPs
- Check if asyncpg is in requirements.txt

### CORS Errors
- Add Hugging Face Space URL to CORS_ORIGINS
- Include both http and https if needed
- Restart Space after updating secrets

## Alternative: Gradio Wrapper (Optional)

If you want a UI in Hugging Face, you can wrap your FastAPI with Gradio:

```python
import gradio as gr
from main import app

# Mount FastAPI
gr.mount_gradio_app(app, path="/api")
```

This gives you both API and a web interface.

## Support
- Hugging Face Docs: https://huggingface.co/docs/hub/spaces
- Community Forum: https://discuss.huggingface.co
