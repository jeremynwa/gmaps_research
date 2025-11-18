#!/bin/bash

echo "🚂 Deploying to Railway..."
echo "========================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm i -g @railway/cli
fi

# Login to Railway
echo ""
echo "🔐 Logging in to Railway..."
railway login

# Link to project (or create new)
echo ""
echo "🔗 Linking to Railway project..."
railway link

# Set environment variables
echo ""
echo "⚙️  Setting environment variables..."
echo "Enter your Anthropic API key:"
read -s ANTHROPIC_KEY
railway variables set ANTHROPIC_API_KEY=$ANTHROPIC_KEY

echo "Enter your Outscraper API key:"
read -s OUTSCRAPER_KEY
railway variables set OUTSCRAPER_API_KEY=$OUTSCRAPER_KEY

# Deploy
echo ""
echo "🚀 Deploying..."
railway up

echo ""
echo "✅ Deployment complete!"
echo "🌐 View your deployment: railway open"