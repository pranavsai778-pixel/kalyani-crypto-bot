import requests
import os
from datetime import datetime
import pytz
from kalyani_analysis import (
    load_models_for_research,
    analyze_top_10_winners_deep,
    analyze_top_10_losers_deep
)
from kalyani_technical import TechnicalAnalyzer
from kalyani_fundamental import FundamentalAnalyzer

COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def fetch_cryptocurrencies():
    """Fetch top 100 cryptocurrencies"""
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
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching: {e}")
        return []

def format_price(price):
    if price is None:
        return "N/A"
    if price >= 1:
        return f"${price:,.2f}"
    else:
        return f"${price:.8f}"

def format_volume(volume):
    if volume is None or volume == 0:
        return "N/A"
    if volume >= 1_000_000_000:
        return f"${volume/1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"${volume/1_000_000:.2f}M"
    else:
        return f"${volume/1_000:.2f}K"

def format_market_cap(market_cap):
    if market_cap is None or market_cap == 0:
        return "N/A"
    if market_cap >= 1_000_000_000:
        return f"${market_cap/1_000_000_000:.2f}B"
    else:
        return f"${market_cap/1_000_000:.2f}M"

def format_daily_report(winners_analysis, losers_analysis, winners_data, losers_data, all_crypto):
    """Format daily deep analysis report"""
    ist_tz = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist_tz).strftime("%Y-%m-%d %H:%M IST")
    
    # Calculate daily stats (midnight to now)
    daily_change_24h = sum([c.get('price_change_percentage_24h', 0) or 0 for c in all_crypto[:10]]) / 10
    
    report = f"""
📅 **KALYANI v5.0 - DAILY DEEP ANALYSIS REPORT**
⏰ {timestamp}
📊 Period: Midnight (00:00) to Now (IST)
🔍 Analysis Type: Deep Fundamental + Technical

**DAILY MARKET OVERVIEW**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Average 24h Change (Top 10): {daily_change_24h:.2f}%

🏆 **TOP 10 WINNERS - DEEP ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for i, coin in enumerate(winners_analysis):
        winner_data = winners_data[i]
        volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(winner_data)
        volatility = FundamentalAnalyzer.analyze_price_volatility(winner_data)
        price_changes = FundamentalAnalyzer.analyze_price_change_periods(winner_data)
        rating = FundamentalAnalyzer.get_fundamental_rating(winner_data, all_crypto)
        
        report += f"""
{coin['rank']}. **{coin['name']}** ({coin['symbol']})
   
   **PRICE INFO:**
   💰 Current: {format_price(coin['price'])}
   📈 24h Change: +{coin['change_24h']}%
   📊 7d Change: {price_changes['7d']['change']}% {price_changes['7d']['signal']}
   📉 30d Change: {price_changes['30d']['change']}% {price_changes['30d']['signal']}
   
   **MARKET DATA:**
   💼 Market Cap: {format_market_cap(coin['market_cap'])}
   📊 Volume: {format_volume(coin['volume'])}
   📉 Vol/MC Ratio: {volume_ratio}%
   
   **FUNDAMENTAL ANALYSIS:**
   ⭐ Rating: {rating}
   ⚡ Volatility: {volatility}
   💪 Vol/MC Health: {FundamentalAnalyzer.get_market_health(volume_ratio)}
   
   **SENTIMENT:**
   💭 {coin['market_sentiment']}
   🧠 Confidence: {coin['confidence']}
"""
    
    report += f"""

💔 **TOP 10 LOSERS - DEEP ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for i, coin in enumerate(losers_analysis):
        loser_data = losers_data[i]
        volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(loser_data)
        volatility = FundamentalAnalyzer.analyze_price_volatility(loser_data)
        price_changes = FundamentalAnalyzer.analyze_price_change_periods(loser_data)
        rating = FundamentalAnalyzer.get_fundamental_rating(loser_data, all_crypto)
        
        report += f"""
{coin['rank']}. **{coin['name']}** ({coin['symbol']})
   
   **PRICE INFO:**
   💰 Current: {format_price(coin['price'])}
   📉 24h Change: {coin['change_24h']}%
   📊 7d Change: {price_changes['7d']['change']}% {price_changes['7d']['signal']}
   📉 30d Change: {price_changes['30d']['change']}% {price_changes['30d']['signal']}
   
   **MARKET DATA:**
   💼 Market Cap: {format_market_cap(coin['market_cap'])}
   📊 Volume: {format_volume(coin['volume'])}
   📉 Vol/MC Ratio: {volume_ratio}%
   
   **FUNDAMENTAL ANALYSIS:**
   ⭐ Rating: {rating}
   ⚡ Volatility: {volatility}
   💪 Vol/MC Health: {FundamentalAnalyzer.get_market_health(volume_ratio)}
   
   **SENTIMENT:**
   💭 {coin['market_sentiment']}
   🧠 Confidence: {coin['confidence']}
"""
    
    report += """

---
🔍 **ANALYSIS LEGEND:**
⭐ Rating = Overall fundamental strength (STRONG/MODERATE/WEAK)
⚡ Volatility = Price stability (Stable/Moderate/Highly Volatile/Extremely Volatile)
📉 Vol/MC = Liquidity indicator (higher % = more liquid)
💭 Sentiment = AI market sentiment analysis
🧠 Confidence = AI confidence score (0-1)

📊 Report Type: DAILY DEEP ANALYSIS
⏱️ Time Window: Midnight (00:00 IST) to Now
🔗 Data: CoinGecko API | 🧠 AI: Hugging Face
    """
    
    return report

def send_to_discord(message):
    """Send message to Discord"""
    if not DISCORD_WEBHOOK_URL:
        return False
    
    try:
        if len(message) > 2000:
            messages = [message[i:i+1900] for i in range(0, len(message), 1900)]
            for msg in messages:
                requests.post(DISCORD_WEBHOOK_URL, json={"content": msg}, timeout=10)
        else:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)
        
        print("✅ Daily report sent to Discord")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_kalyani_daily():
    """Run daily deep analysis"""
    print("\n" + "="*70)
    print("📅 KALYANI v5.0 - DAILY DEEP ANALYSIS")
    print("="*70 + "\n")
    
    print("📥 Loading AI models for deep analysis...")
    model = load_models_for_research()
    
    if model is None:
        print("❌ Failed to load model")
        return False
    
    crypto_data = fetch_cryptocurrencies()
    if not crypto_data:
        print("❌ Failed to fetch data")
        return False
    
    # Get top 10
    winners = sorted(crypto_data, key=lambda x: x.get('price_change_percentage_24h', 0) or 0, reverse=True)[:10]
    losers = sorted(crypto_data, key=lambda x: x.get('price_change_percentage_24h', 0) or 0)[:10]
    
    print("🧠 Deep analysis in progress...")
    winners_analysis = analyze_top_10_winners_deep(winners, model)
    losers_analysis = analyze_top_10_losers_deep(losers, model)
    
    report = format_daily_report(winners_analysis, losers_analysis, winners, losers, crypto_data)
    
    print(report)
    send_to_discord(report)

if __name__ == "__main__":
    run_kalyani_daily()
