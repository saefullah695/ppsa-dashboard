#!/bin/bash

echo "🚀 Deploying PPSA Dashboard..."

# Deploy Worker
echo "📦 Deploying Cloudflare Worker..."
cd worker
npm install
wrangler deploy

# Deploy Frontend
echo "🌐 Building and deploying frontend..."
cd ../frontend
npm install
npm run build

# Deploy to Cloudflare Pages (if configured)
# You would need to set up Cloudflare Pages for this

echo "✅ Deployment complete!"
echo "🌍 Frontend: https://your-frontend.pages.dev"
echo "🔧 Worker: https://ppsa-dashboard.your-subdomain.workers.dev"
