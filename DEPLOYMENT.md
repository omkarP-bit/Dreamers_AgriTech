# Deployment Guide - FasalMitra

## Backend Deployment (Render) ✅ COMPLETED

**Live URL**: https://farm-ai-assistant.onrender.com

### Status
- ✅ Backend deployed successfully
- ✅ MongoDB connected
- ✅ CORS configured for Vercel
- ✅ Environment variables set

### Test Backend
```bash
curl https://farm-ai-assistant.onrender.com/health
curl https://farm-ai-assistant.onrender.com/
```

### API Documentation
Visit: https://farm-ai-assistant.onrender.com/docs

---

## Frontend Deployment (Vercel)

### Option 1: Vercel Dashboard (Recommended)

1. **Go to Vercel**: https://vercel.com/new

2. **Import Repository**:
   - Click "Import Git Repository"
   - Select: `omkarP-bit/Dreamers_AgriTech`
   - Click "Import"

3. **Configure Project**:
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

4. **Environment Variables** (Optional):
   ```
   VITE_API_URL=https://farm-ai-assistant.onrender.com/api
   ```

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your app will be live!

### Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from frontend directory
cd frontend
vercel --prod

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? dreamers-agritech
# - Directory? ./
# - Override settings? No
```

---

## Testing Full Stack

Once frontend is deployed:

1. **Visit your Vercel URL**: https://your-app.vercel.app
2. **Register a new account**
3. **Test the chat functionality**
4. **Create a crop season**

---

## Troubleshooting

### If CORS errors occur:
The backend is already configured to allow all `*.vercel.app` domains.
If you use a custom domain, add it to `backend/app.py`:
```python
allowed_origins = [
    "https://your-custom-domain.com",
]
```

### If API calls fail:
Check that `frontend/src/api.js` has the correct backend URL:
```javascript
const API_BASE_URL = 'https://farm-ai-assistant.onrender.com/api';
```

### If build fails on Vercel:
1. Check Node.js version in `package.json`:
   ```json
   "engines": {
     "node": ">=18.0.0"
   }
   ```
2. Ensure all dependencies are in `package.json`
3. Check Vercel build logs for specific errors

---

## Important Notes

- **Render Free Tier**: Backend sleeps after 15 min inactivity (30s cold start)
- **Vercel Free Tier**: Unlimited bandwidth, 100GB/month
- **MongoDB Atlas**: Free tier with 512MB storage
- **Auto-Deploy**: Both platforms auto-deploy on git push to main

---

## Quick Deploy Commands

```bash
# Push changes to trigger auto-deploy
git add .
git commit -m "Update for deployment"
git push origin main

# Both Render and Vercel will auto-deploy!
```

---

## Support

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- MongoDB Atlas: https://www.mongodb.com/docs/atlas/

---

## Hackathon Demo URLs

**Backend API**: https://farm-ai-assistant.onrender.com
**API Docs**: https://farm-ai-assistant.onrender.com/docs
**Frontend**: [Deploy to get URL]

Good luck with your hackathon! 🚀
