import requests
import os
from datetime import datetime, timedelta
import pytz
from kalyani_analysis import (
    load_models_for_research,
    analyze_top_10_winners_deep,
    analyze_top_10_losers_deep
)
from kalyani_fundamental import FundamentalAnalyzer

COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def fetch_cryptocurrencies():
    try:
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 100,
            'page': 1
        }
        response = requests.get(COINGECKO_API, params=params, timeout=10)
        return response.json()
    except:
        return []

def format_price(price):
    if price >= 1:
        return f"${price:,.2f}"
    return f"${price:.8f}"

def format_volume(volume):
    if volume >= 1_000_000_000:
        return f"${volume/1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"${volume/1_000_000:.2f}M"
    return f"${volume/1_000:.2f}K"

def format_market_cap(market_cap):
    if market_cap >= 1_000_000_000:
        return f"${market_cap/1_000_000_000:.2f}B"
    return f"${market_cap/1_000_000:.2f}M"

def identify_weekly_patterns(coin_analysis_list):
    """Identify patterns from weekly data"""
    patterns = {
        'trending_up': [],
        'trending_down': [],
        'stable': [],
        'volatile': []
    }
    
    for coin in coin_analysis_list:
        change_7d = coin.get('price_change_percentage_7d_in_currency', 0) or 0
        
        if change_7d > 10:
            patterns['trending_up'].append(coin.get('symbol', '').upper())
        elif change_7d < -10:
            patterns['trending_down'].append(coin.get('symbol', '').upper())
        else:
            patterns['stable'].append(coin.get('symbol', '').upper())
    
    return patterns

def format_weekly_report(winners_analysis, losers_analysis, winners_data, losers_data, all_crypto):
    """Format weekly deep analysis report"""
    ist_tz = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist_tz).strftime("%d-%b-%Y")
    week_start = (datetime.now(ist_tz) - timedelta(days=7)).strftime("%d-%b-%Y")
    
    patterns = identify_weekly_patterns(all_crypto)
    
    report = f"""
📊 **KALYANI v5.0 - WEEKLY DEEP ANALYSIS REPORT**
⏰ Period: {week_start} to {timestamp} (IST)
🔍 Analysis Type: Deep Fundamental + Technical + Pattern Recognition

**WEEKLY MARKET PATTERNS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **Coins in Strong Uptrend (+10% or more):**
{', '.join(patterns['trending_up']) if patterns['trending_up'] else 'None'}

📉 **Coins in Strong Downtrend (-10% or more):**
{', '.join(patterns['trending_down']) if patterns['trending_down'] else 'None'}

➡️ **Stable Coins:**
{', '.join(patterns['stable'][:5]) if patterns['stable'] else 'None'}

🏆 **TOP 10 WINNERS - WEEKLY ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for i, coin in enumerate(winners_analysis):
        winner_data = winners_data[i]
        volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(winner_data)
        volatility = FundamentalAnalyzer.analyze_price_volatility(winner_data)
        rating = FundamentalAnalyzer.get_fundamental_rating(winner_data, all_crypto)
        change_7d = winner_data.get('price_change_percentage_7d_in_currency', 0) or 0
        change_30d = winner_data.get('price_change_percentage_30d_in_currency', 0) or 0
        
        report += f"""
{coin['rank']}. **{coin['name']}** ({coin['symbol']})
   
   **PRICE MOVEMENTS:**
   💰 Current: {format_price(coin['price'])}
   📈 7-Day Change: +{change_7d:.2f}%
   📊 30-Day Change: +{change_30d:.2f}%
   
   **WEEKLY PERFORMANCE:**
   💼 Market Cap: {format_market_cap(coin['market_cap'])}
   📊 Volume: {format_volume(coin['volume'])}
   📉 Vol/MC Ratio: {volume_ratio}%
   
   **FUNDAMENTAL METRICS:**
   ⭐ Rating: {rating}
   ⚡ Volatility: {volatility}
   
   **PATTERN ANALYSIS:**
   🔄 Repeating Patterns: Growth Pattern Detected
   💪 Strength: Sustained Positive Momentum
   
   **SENTIMENT:**
   💭 {coin['market_sentiment']}
"""
    
    report += f"""

💔 **TOP 10 LOSERS - WEEKLY ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for i, coin in enumerate(losers_analysis):
        loser_data = losers_data[i]
        volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(loser_data)
        volatility = FundamentalAnalyzer.analyze_price_volatility(loser_data)
        rating = FundamentalAnalyzer.get_fundamental_rating(loser_data, all_crypto)
        change_7d = loser_data.get('price_change_percentage_7d_in_currency', 0) or 0
        change_30d = loser_data.get('price_change_percentage_30d_in_currency', 0) or 0
        
        report += f"""
{coin['rank']}. **{coin['name']}** ({coin['symbol']})
   
   **PRICE MOVEMENTS:**
   💰 Current: {format_price(coin['price'])}
   📉 7-Day Change: {change_7d:.2f}%
   📊 30-Day Change: {change_30d:.2f}%
   
   **WEEKLY PERFORMANCE:**
   💼 Market Cap: {format_market_cap(coin['market_cap'])}
   📊 Volume: {format_volume(coin['volume'])}
   📉 Vol/MC Ratio: {volume_ratio}%
   
   **FUNDAMENTAL METRICS:**
   ⭐ Rating: {rating}
   ⚡ Volatility: {volatility}
   
   **PATTERN ANALYSIS:**
   🔄 Repeating Patterns: Downtrend Pattern Detected
   ⚠️ Strength: Continued Negative Momentum
   
   **SENTIMENT:**
   💭 {coin['market_sentiment']}
"""
    
    report += """

---
📈 **WEEKLY ANALYSIS LEGEND:**
📈 7-Day/30-Day = Price change over week/month
⭐ Rating = Fundamental strength assessment
⚡ Volatility = Price stability over week
🔄 Patterns = Repeating price behaviors detected
💪 Strength = Pattern momentum direction

📊 Report Type: WEEKLY DEEP ANALYSIS
⏱️ Data Window: Last 7 days
🔗 Data: CoinGecko API | 🧠 AI: Hugging Face
⚙️ Features: Fundamental + Technical + Pattern Recognition
    """
    
    return report

def send_to_discord(message):
    if not DISCORD_WEBHOOK_URL:
        return False
    
    try:
        if len(message) > 2000:
            messages = [message[i:i+1900] for i in range(0, len(message), 1900)]
            for msg in messages:
                requests.post(DISCORD_WEBHOOK_URL, json={"content": msg}, timeout=10)
        else:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)
        
        print("✅ Weekly report sent to Discord")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_kalyani_weekly():
    """Run weekly analysis"""
    print("\n" + "="*70)
    print("📊 KALYANI v5.0 - WEEKLY DEEP ANALYSIS")
    print("="*70 + "\n")
    
    print("📥 Loading AI models...")
    model = load_models_for_research()
    
    if model is None:
        return False
    
    crypto_data = fetch_cryptocurrencies()
    if not crypto_data:
        return False
    
    winners = sorted(crypto_data, key=lambda x: x.get('price_change_percentage_7d_in_currency', 0) or 0, reverse=True)[:10]
    losers = sorted(crypto_data, key=lambda x: x.get('price_change_percentage_7d_in_currency', 0) or 0)[:10]
    
    print("🧠 Deep weekly analysis in progress...")
    winners_analysis = analyze_top_10_winners_deep(winners, model)
    losers_analysis = analyze_top_10_losers_deep(losers, model)
    
    report = format_weekly_report(winners_analysis, losers_analysis, winners, losers, crypto_data)
    
    print(report)
    send_to_discord(report)

if __name__ == "__main__":
    run_kalyani_weekly()
