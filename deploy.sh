#!/bin/bash

echo "🚀 Qasa Bot Deployment Script"
echo "=============================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit"
fi

echo ""
echo "Choose your deployment platform:"
echo "1) Railway (Recommended - Free)"
echo "2) Render (Free)"
echo "3) Heroku (Paid)"
echo "4) DigitalOcean (VPS - $5/month)"
echo "5) AWS EC2 (Free tier available)"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🚂 Deploying to Railway..."
        echo "1. Go to https://railway.app"
        echo "2. Sign up and connect your GitHub"
        echo "3. Create a new project from your GitHub repo"
        echo "4. Add these environment variables:"
        echo "   - GMAIL_USER=your-email@gmail.com"
        echo "   - GMAIL_PASSWORD=your-app-password"
        echo "   - QASA_EMAIL=your-qasa-email"
        echo "   - QASA_PASSWORD=your-qasa-password"
        echo "5. Deploy!"
        ;;
    2)
        echo "🎨 Deploying to Render..."
        echo "1. Go to https://render.com"
        echo "2. Sign up and connect your GitHub"
        echo "3. Create a new Web Service"
        echo "4. Select your repository"
        echo "5. Add environment variables (same as Railway)"
        echo "6. Deploy!"
        ;;
    3)
        echo "🦸 Deploying to Heroku..."
        if ! command -v heroku &> /dev/null; then
            echo "Installing Heroku CLI..."
            curl https://cli-assets.heroku.com/install.sh | sh
        fi
        echo "1. Run: heroku login"
        echo "2. Run: heroku create your-qasa-bot"
        echo "3. Set environment variables:"
        echo "   heroku config:set GMAIL_USER=your-email@gmail.com"
        echo "   heroku config:set GMAIL_PASSWORD=your-app-password"
        echo "   heroku config:set QASA_EMAIL=your-qasa-email"
        echo "   heroku config:set QASA_PASSWORD=your-qasa-password"
        echo "4. Run: heroku deploy"
        ;;
    4)
        echo "🐳 Deploying to DigitalOcean..."
        echo "1. Create a droplet at https://digitalocean.com"
        echo "2. SSH into your server: ssh root@your-server-ip"
        echo "3. Install Docker:"
        echo "   curl -fsSL https://get.docker.com -o get-docker.sh"
        echo "   sh get-docker.sh"
        echo "4. Clone and run:"
        echo "   git clone https://github.com/your-username/qasa-bot.git"
        echo "   cd qasa-bot"
        echo "   docker-compose up -d"
        ;;
    5)
        echo "☁️ Deploying to AWS EC2..."
        echo "1. Launch EC2 instance (t2.micro for free tier)"
        echo "2. SSH into your instance"
        echo "3. Follow the same steps as DigitalOcean"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Setup complete! Your bot will run 24/7."
echo "📧 Make sure to set up your Gmail app password first!"
echo "🔗 Check the README.md for detailed instructions." 