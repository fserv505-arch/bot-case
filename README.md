# Qasa Apartment Scraper Bot

A Python bot that automatically monitors Qasa.se for new apartment listings and sends email notifications when new properties are found.

## Features

- 🔍 Monitors Qasa.se for new furnished apartments in Stockholm
- 📧 Sends email notifications for new listings
- 💰 Filters by price (max 12,300 SEK)
- 🏠 Filters by room count (max 4 rooms)
- 🕐 Runs during active hours (7 AM - 11 PM) with random intervals (5-40 minutes)
- 📝 Tracks seen listings to avoid duplicates
- ⏰ Configurable active hours via environment variables

## Deployment Options

### Option 1: Railway (Recommended - Free Tier)

Railway is a simple platform that's perfect for this type of bot.

1. **Sign up** at [railway.app](https://railway.app)
2. **Connect your GitHub** repository
3. **Deploy** by pushing to GitHub

```bash
# Add Railway configuration
railway login
railway init
railway up
```

### Option 2: Render (Free Tier)

1. **Sign up** at [render.com](https://render.com)
2. **Create a new Web Service**
3. **Connect your GitHub** repository
4. **Set environment variables**:
   - `GMAIL_USER`: your-email@gmail.com
   - `GMAIL_PASSWORD`: your-app-password
   - `QASA_EMAIL`: your-qasa-email
   - `QASA_PASSWORD`: your-qasa-password

### Option 3: Heroku (Paid)

1. **Install Heroku CLI**
2. **Create app**:
```bash
heroku create your-qasa-bot
heroku config:set GMAIL_USER=your-email@gmail.com
heroku config:set GMAIL_PASSWORD=your-app-password
heroku config:set QASA_EMAIL=your-qasa-email
heroku config:set QASA_PASSWORD=your-qasa-password
heroku deploy
```

### Option 4: DigitalOcean Droplet (VPS)

1. **Create a droplet** ($5-10/month)
2. **SSH into your server**:
```bash
ssh root@your-server-ip
```

3. **Install Docker**:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

4. **Clone and run**:
```bash
git clone https://github.com/your-username/qasa-bot.git
cd qasa-bot
docker-compose up -d
```

### Option 5: AWS EC2 (Free Tier Available)

1. **Launch EC2 instance** (t2.micro is free tier)
2. **Connect via SSH**
3. **Install Docker** and run as above

## Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
playwright install
```

2. **Set up config**:
Edit `config.yaml` with your credentials

3. **Run locally**:
```bash
python main.py
```

## Environment Variables

For deployment, set these environment variables:

- `GMAIL_USER`: Your Gmail address
- `GMAIL_PASSWORD`: Your Gmail app password (not regular password)
- `QASA_EMAIL`: Your Qasa account email
- `QASA_PASSWORD`: Your Qasa account password
- `MESSAGE_TO_OWNER`: Custom message to send to landlords
- `ACTIVE_START_HOUR`: Hour to start monitoring (default: 7 for 7 AM)
- `ACTIVE_END_HOUR`: Hour to stop monitoring (default: 23 for 11 PM)

## Gmail Setup

1. **Enable 2-factor authentication** on your Google account
2. **Generate an app password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Use the app password** in your configuration

## Security Notes

- Never commit your `config.yaml` to version control
- Use environment variables in production
- Consider using a dedicated Gmail account for the bot
- Regularly rotate your app passwords

## Scheduling

The bot runs on a smart schedule:

- **Active Hours**: 7 AM to 11 PM (configurable)
- **During Active Hours**: Checks every 5-40 minutes (random intervals)
- **Outside Active Hours**: Sleeps until next active period
- **Benefits**: 
  - Saves resources and costs
  - More likely to find listings when people are active
  - Reduces server load during off-hours

### Customizing Active Hours

Set these environment variables to change the schedule:

```bash
# Example: Run from 8 AM to 10 PM
ACTIVE_START_HOUR=8
ACTIVE_END_HOUR=22

# Example: Run 24/7 (not recommended)
ACTIVE_START_HOUR=0
ACTIVE_END_HOUR=23
```

## Monitoring

The bot will:
- Print logs to console
- Send email notifications for new listings
- Save seen listing IDs to `seen_listings.json`
- Show current active hours and sleep status

## Troubleshooting

### Common Issues

1. **Playwright browser issues**: Make sure you're using the Docker setup or have proper browser dependencies
2. **Gmail authentication**: Ensure you're using an app password, not your regular password
3. **Rate limiting**: The bot includes random delays to avoid being blocked

### Logs

Check logs with:
```bash
# Docker
docker logs qasa-bot

# Railway
railway logs

# Render
# Check in the Render dashboard
```

## Cost Comparison

| Platform | Cost | Pros | Cons |
|----------|------|------|------|
| Railway | Free tier | Easy setup, good free tier | Limited resources |
| Render | Free tier | Good free tier, easy setup | Can be slow |
| Heroku | $7/month | Reliable, good performance | Paid only |
| DigitalOcean | $5-10/month | Full control, good performance | Requires setup |
| AWS EC2 | Free tier available | Scalable, powerful | Complex setup |

## Recommended Setup

For beginners: **Railway** (free, easy)
For reliability: **DigitalOcean** ($5/month)
For scalability: **AWS EC2** (free tier available) 