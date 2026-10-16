import requests
import json
import os
from datetime import datetime
import pytz
from kalyani_analysis import (
    load_models_for_hourly,
    analyze_top_10_winners_quick,
    analyze_top_10_losers_quick
)
from kalyani_technical import TechnicalAnalyzer
from kalyani_fundamental import FundamentalAnalyzer

# API URLs
COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def fetch_cryptocurrencies():
    """Fetch top 100 cryptocurrencies from CoinGecko"""
    print("🔄 Fetching cryptocurrency data from CoinGecko...")
    try:
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 100,
            'page': 1,
            'sparkline': False
        }
        response = requests.get(COINGECKO_API, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Successfully fetched {len(data)} cryptocurrencies")
        return data
    except Exception as e:
        print(f"❌ Error fetching cryptocurrencies: {e}")
        return []

def get_top_10_winners_losers(crypto_data):
    """Get top 10 winners and top 10 losers"""
    if not crypto_data:
        print("❌ No crypto data available")
        return [], []
    
    sorted_coins = sorted(
        crypto_data,
        key=lambda x: x.get('price_change_percentage_24h', 0) or 0,
        reverse=True
    )
    
    winners = sorted_coins[:10]
    losers = sorted_coins[-10:]
    losers = list(reversed(losers))
    
    print(f"✅ Found {len(winners)} winners and {len(losers)} losers")
    return winners, losers

def format_price(price):
    """Format price nicely"""
    if price is None:
        return "N/A"
    if price >= 1:
        return f"${price:,.2f}"
    else:
        return f"${price:.8f}"

def format_volume(volume):
    """Format trading volume"""
    if volume is None or volume == 0:
        return "N/A"
    if volume >= 1_000_000_000:
        return f"${volume/1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"${volume/1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"${volume/1_000:.2f}K"
    else:
        return f"${volume:.2f}"

def format_market_cap(market_cap):
    """Format market cap"""
    if market_cap is None or market_cap == 0:
        return "N/A"
    if market_cap >= 1_000_000_000_000:
        return f"${market_cap/1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap/1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap/1_000_000:.2f}M"
    else:
        return f"${market_cap:.2f}"

def calculate_market_health(coin):
    """Calculate market health indicators"""
    volume = coin.get('total_volume', 0) or 0
    market_cap = coin.get('market_cap', 0) or 0
    
    if market_cap > 0:
        volume_ratio = (volume / market_cap) * 100
        if volume_ratio > 10:
            return "🔥 High Activity"
        elif volume_ratio > 5:
            return "📈 Active"
        elif volume_ratio > 1:
            return "➡️ Normal"
        else:
            return "❄️ Low Activity"
    return "❓ Unknown"

def format_hourly_report(winners_analysis, losers_analysis, winners_data, losers_data, all_crypto):
    """Format the hourly report for Discord"""
    ist_tz = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist_tz).strftime("%Y-%m-%d %H:%M IST")
    
    # Build winners section
    winners_text = "🏆 **TOP 10 WINNERS (24h)**\n"
    winners_text += "=" * 70 + "\n"
    for i, coin in enumerate(winners_analysis):
        winner_data = winners_data[i]
        market_health = calculate_market_health(winner_data)
        market_cap = format_market_cap(winner_data.get('market_cap'))
        volume = format_volume(winner_data.get('total_volume'))
        volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(winner_data)
        
        winners_text += f"\n{coin['rank']}. **{coin['name']}** ({coin['symbol']})\n"
        winners_text += f"   💰 Price: {format_price(coin['price'])}\n"
        winners_text += f"   📈 Change: +{coin['change_24h']}%\n"
        winners_text += f"   💼 Market Cap: {market_cap}\n"
        winners_text += f"   📊 Volume: {volume}\n"
        winners_text += f"   📉 Vol/MC Ratio: {volume_ratio}%\n"
        winners_text += f"   🏥 Health: {market_health}\n"
        winners_text += f"   💭 Sentiment: {coin['market_sentiment']}\n"
    
    # Build losers section
    losers_text = "\n💔 **TOP 10 LOSERS (24h)**\n"
    losers_text += "=" * 70 + "\n"
    for i, coin in enumerate(losers_analysis):
        loser_data = losers_data[i]
        market_health = calculate_market_health(loser_data)
        market_cap = format_market_cap(loser_data.get('market_cap'))
        volume = format_volume(loser_data.get('total_volume'))
        volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(loser_data)
        
        losers_text += f"\n{coin['rank']}. **{coin['name']}** ({coin['symbol']})\n"
        losers_text += f"   💰 Price: {format_price(coin['price'])}\n"
        losers_text += f"   📉 Change: {coin['change_24h']}%\n"
        losers_text += f"   💼 Market Cap: {market_cap}\n"
        losers_text += f"   📊 Volume: {volume}\n"
        losers_text += f"   📉 Vol/MC Ratio: {volume_ratio}%\n"
        losers_text += f"   🏥 Health: {market_health}\n"
        losers_text += f"   💭 Sentiment: {coin['market_sentiment']}\n"
    
    report = f"""
🤖 **KALYANI v5.0 - HOURLY MARKET REPORT**
⏰ {timestamp}
📊 Data Type: Live 24-Hour Window

{winners_text}

{losers_text}

---
📚 **Legend:**
💰 Price = Current USD price
📈/📉 Change = 24-hour % change
💼 Market Cap = Total market capitalization
📊 Volume = 24-hour trading volume
📉 Vol/MC = Volume to Market Cap ratio (higher = more liquid)
🏥 Health = Market activity level
💭 Sentiment = AI-powered sentiment analysis

🔗 Data: CoinGecko API | 🧠 AI: Hugging Face Transformers
⏱️ Report Type: Hourly (Live Data)
    """
    
    return report

def send_to_discord(message):
    """Send message to Discord webhook"""
    if not DISCORD_WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK_URL not found in environment variables")
        return False
    
    try:
        # Discord has message length limit, split if needed
        if len(message) > 2000:
            messages = [message[i:i+1900] for i in range(0, len(message), 1900)]
            for msg in messages:
                payload = {"content": msg}
                requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        else:
            payload = {"content": message}
            response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
            response.raise_for_status()
        
        print("✅ Message sent to Discord successfully")
        return True
    except Exception as e:
        print(f"❌ Error sending to Discord: {e}")
        return False

def run_kalyani_hourly():
    """Main function to run KALYANI hourly bot"""
    print("\n" + "="*70)
    print("🚀 KALYANI v5.0 CRYPTO BOT - HOURLY REPORT")
    print("="*70 + "\n")
    
    # Load AI model
    print("📥 Loading AI model...")
    model = load_models_for_hourly()
    
    if model is None:
        print("❌ Failed to load model. Exiting.")
        return False
    
    # Fetch crypto data
    crypto_data = fetch_cryptocurrencies()
    if not crypto_data:
        print("❌ Failed to fetch crypto data. Exiting.")
        return False
    
    # Get winners and losers
    winners, losers = get_top_10_winners_losers(crypto_data)
    
    if not winners or not losers:
        print("❌ Failed to identify winners and losers. Exiting.")
        return False
    
    # Analyze winners and losers
    print("🧠 Analyzing winners...")
    winners_analysis = analyze_top_10_winners_quick(winners, model)
    
    print("🧠 Analyzing losers...")
    losers_analysis = analyze_top_10_losers_quick(losers, model)
    
    if not winners_analysis or not losers_analysis:
        print("❌ Analysis failed. Exiting.")
        return False
    
    # Format and send report
    report = format_hourly_report(winners_analysis, losers_analysis, winners, losers, crypto_data)
    
    print("\n📋 Report:\n")
    print(report)
    
    # Send to Discord
    if send_to_discord(report):
        print("\n✅ KALYANI HOURLY BOT COMPLETED SUCCESSFULLY")
        return True
    else:
        print("\n❌ KALYANI BOT FAILED TO SEND REPORT")
        return False

if __name__ == "__main__":
    run_kalyani_hourly()
