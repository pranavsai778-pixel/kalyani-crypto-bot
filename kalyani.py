import requests
import json
import os
from datetime import datetime
from kalyani_analysis import (
    load_models_for_hourly,
    analyze_top_10_winners_quick,
    analyze_top_10_losers_quick
)

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
    
    # Sort by 24h price change
    sorted_coins = sorted(
        crypto_data,
        key=lambda x: x.get('price_change_percentage_24h', 0) or 0,
        reverse=True
    )
    
    # Top 10 winners
    winners = sorted_coins[:10]
    
    # Top 10 losers (reverse sort)
    losers = sorted_coins[-10:]
    losers = list(reversed(losers))
    
    print(f"✅ Found {len(winners)} winners and {len(losers)} losers")
    return winners, losers

def format_hourly_report(winners_analysis, losers_analysis):
    """Format the hourly report for Discord"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    # Build winners section
    winners_text = "🏆 **TOP 10 WINNERS (24h)**\n"
    for coin in winners_analysis:
        winners_text += f"\n{coin['rank']}. **{coin['name']}** ({coin['symbol']})\n"
        winners_text += f"   💰 ${coin['price']:.6f}\n"
        winners_text += f"   📈 +{coin['change_24h']}%\n"
        winners_text += f"   💭 {coin['market_sentiment']}\n"
    
    # Build losers section
    losers_text = "💔 **TOP 10 LOSERS (24h)**\n"
    for coin in losers_analysis:
        losers_text += f"\n{coin['rank']}. **{coin['name']}** ({coin['symbol']})\n"
        losers_text += f"   💰 ${coin['price']:.6f}\n"
        losers_text += f"   📉 {coin['change_24h']}%\n"
        losers_text += f"   💭 {coin['market_sentiment']}\n"
    
    report = f"""
🤖 **KALYANI v5.0 - Crypto Market Report**
⏰ {timestamp}

{winners_text}

{losers_text}

---
📊 *AI-Powered Analysis by KALYANI*
🔗 Data: CoinGecko API | 🧠 Models: Hugging Face Transformers
    """
    
    return report

def send_to_discord(message):
    """Send message to Discord webhook"""
    if not DISCORD_WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK_URL not found in environment variables")
        return False
    
    try:
        payload = {
            "content": message
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Message sent to Discord successfully")
        return True
    except Exception as e:
        print(f"❌ Error sending to Discord: {e}")
        return False

def run_kalyani_hourly():
    """Main function to run KALYANI hourly bot"""
    print("\n" + "="*50)
    print("🚀 KALYANI v5.0 CRYPTO BOT STARTED")
    print("="*50 + "\n")
    
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
    report = format_hourly_report(winners_analysis, losers_analysis)
    
    print("\n📋 Report:\n")
    print(report)
    
    # Send to Discord
    if send_to_discord(report):
        print("\n✅ KALYANI BOT COMPLETED SUCCESSFULLY")
        return True
    else:
        print("\n❌ KALYANI BOT FAILED TO SEND REPORT")
        return False

if __name__ == "__main__":
    run_kalyani_hourly()
