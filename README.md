# 🤖 KALYANI v5.0 - Automated Cryptocurrency Market Monitoring Agent

Automated Cryptocurrency Market Monitoring Agent - Real-time crypto analysis with AI-powered insights, hourly market reports, and Discord alerts using Hugging Face transformers and open-source models.

---

## ✨ Features

- ⏰ **Hourly Automated Updates** - Runs automatically every hour on GitHub Actions
- 🏆 **Top 10 Winners & Losers** - Analyzes top 10 winners and top 10 losers from top 100 cryptocurrencies
- 🧠 **AI-Powered Analysis** - Uses Hugging Face open-source models for sentiment analysis
- 💬 **Discord Integration** - Sends formatted reports directly to your Discord server
- 🚀 **100% Free Forever** - No credit card required, costs ₹0 forever
- ⚡ **Fast Analysis** - Completes hourly analysis in 1-2 minutes
- 📊 **Real-time Data** - Fetches live cryptocurrency data from CoinGecko API

---

## 🛠️ Setup Instructions

### Prerequisites
- GitHub account (free)
- Discord account and server
- Hugging Face account (free, no API key needed)

### Step 1: Create GitHub Repository

1. Go to github.com
2. Click **"New"** to create new repository
3. Repository name: `kalyani-crypto-bot`
4. Description: `Automated Cryptocurrency Market Monitoring Agent - Real-time crypto analysis with AI-powered insights, hourly market reports, and Discord alerts using Hugging Face transformers and open-source models.`
5. Make it **Public**
6. Add README: Yes
7. Add .gitignore (Python): Yes
8. Click **"Create repository"**

### Step 2: Set Up Discord Webhook

1. Go to discord.com and log in
2. Go to your server: **kalyani-crypto-bot**
3. Right-click on **#crypto-alerts** channel
4. Click **"Edit channel"**
5. Click **"Integrations"** → **"Webhooks"**
6. Click **"New Webhook"**
7. Name it: `KALYANI`
8. Click **"Copy Webhook URL"**
9. Save this URL somewhere safe

### Step 3: Add GitHub Secrets

1. Go to your GitHub repo: **kalyani-crypto-bot**
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Name: `DISCORD_WEBHOOK_URL`
5. Value: Paste your Discord webhook URL
6. Click **"Add secret"**

*Optional:* If you have a Gemini API key, add it with name `GEMINI_API_KEY`

### Step 4: Upload 5 Files to GitHub

Upload these files to your repository:

1. **requirements.txt** - Python dependencies (ROOT level)
2. **kalyani_analysis.py** - AI analysis module (ROOT level)
3. **kalyani.py** - Main bot code (ROOT level)
4. **.github/workflows/kalyani.yml** - GitHub Actions scheduler (NESTED at .github/workflows/)
5. **README.md** - Documentation (EDIT existing, don't create new)

### Step 5: Test the Bot

1. Go to your GitHub repo
2. Click **"Actions"** tab
3. Click **"KALYANI Crypto Bot"** workflow
4. Click **"Run workflow"** → **"Run workflow"** button
5. Wait 2-3 minutes (first run downloads AI models)
6. Check your Discord #crypto-alerts channel for the report

---

## 📁 File Structure
