---
description: How to deploy MovExplainer to Render (free tier)
---

# Deploy to Render

## Prerequisites
- Groq API key from [console.groq.com](https://console.groq.com) (free)
- GitHub repo with latest code pushed

## Steps

1. **Push to GitHub**
   ```powershell
   git add .
   git commit -m "Add Dockerfile and render.yaml for deployment"
   git push
   ```

2. **Create Render Web Service**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click **New** → **Web Service**
   - Connect your GitHub repo (`MovExplainer`)
   - Render will auto-detect the Dockerfile

3. **Configure Environment Variables** (in Render dashboard)
   - `LLM_PROVIDER` = `groq`
   - `GROQ_API_KEY` = your key from console.groq.com
   - `STOCKFISH_PATH` = `/usr/games/stockfish`

4. **Deploy**
   - Click **Create Web Service**
   - Wait for build (~2-3 minutes)

5. **Test**
   - Visit `https://your-app.onrender.com`
   - Try the web UI with a chess position

## Notes
- Free tier spins down after 15 min inactivity (first request takes ~30s)
- Logs available in Render dashboard under "Logs" tab
- To redeploy: push to GitHub → Render auto-deploys
