#!/bin/bash

echo "🚀 Railway Deployment Setup"
echo "=========================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized. Please run: git init"
    exit 1
fi

echo ""
echo "📋 Follow these steps:"
echo ""
echo "1️⃣  Create a new GitHub repository:"
echo "   - Go to https://github.com"
echo "   - Click '+' → New repository"
echo "   - Name it 'qasa-bot'"
echo "   - Make it Public"
echo "   - Don't initialize with README"
echo ""

read -p "2️⃣  Enter your GitHub username: " github_username

echo ""
echo "3️⃣  Running git commands..."

# Remove existing remote if any
git remote remove origin 2>/dev/null

# Add new remote
git remote add origin https://github.com/$github_username/qasa-bot.git
git branch -M main

echo "4️⃣  Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "5️⃣  Deploy on Railway:"
echo "   - Go to https://railway.app"
echo "   - Sign up/Login with GitHub"
echo "   - Click 'New Project'"
echo "   - Select 'Deploy from GitHub repo'"
echo "   - Choose your qasa-bot repository"
echo "   - Click 'Deploy'"
echo ""
echo "6️⃣  Add environment variables in Railway:"
echo "   GMAIL_USER=federicocomel1@gmail.com"
echo "   GMAIL_PASSWORD=sxut pnec phde lhyb"
echo "   QASA_EMAIL=federicocomel1@gmail.com"
echo "   QASA_PASSWORD=hypgu1-zegriz-marfoK"
echo "   ACTIVE_START_HOUR=7"
echo "   ACTIVE_END_HOUR=23"
echo ""
echo "🎉 Your bot will be running 24/7 (7 AM - 11 PM)!" 