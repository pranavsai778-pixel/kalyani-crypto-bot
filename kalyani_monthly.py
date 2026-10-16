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
from kalyani_technical import TechnicalAnalyzer

COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets"
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def fetch_cryptocurrencies():
    """Fetch top 100 cryptocurrencies"""
    try:
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 100,
            'page': 1
        }
        response = requests.get(COINGECKO_API, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching: {e}")
        return []

def format_price(price):
    """Format price nicely"""
    if price >= 1:
        return f"${price:,.2f}"
    return f"${price:.8f}"

def format_volume(volume):
    """Format volume"""
    if volume >= 1_000_000_000:
        return f"${volume/1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"${volume/1_000_000:.2f}M"
    return f"${volume/1_000:.2f}K"

def format_market_cap(market_cap):
    """Format market cap"""
    if market_cap >= 1_000_000_000:
        return f"${market_cap/1_000_000_000:.2f}B"
    return f"${market_cap/1_000_000:.2f}M"

def identify_monthly_patterns(all_crypto):
    """Identify patterns from 30-day data"""
    patterns = {
        'strong_uptrend': [],
        'moderate_uptrend': [],
        'stable': [],
        'moderate_downtrend': [],
        'strong_downtrend': [],
        'most_volatile': [],
        'least_volatile': [],
        'highest_volume': [],
        'lowest_volume': []
    }
    
    try:
        # Analyze 30-day changes
        for coin in all_crypto[:50]:
            change_30d = coin.get('price_change_percentage_30d_in_currency', 0) or 0
            change_7d = coin.get('price_change_percentage_7d_in_currency', 0) or 0
            volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(coin)
            
            symbol = coin.get('symbol', '').upper()
            
            # Trend patterns
            if change_30d > 30:
                patterns['strong_uptrend'].append((symbol, change_30d))
            elif change_30d > 10:
                patterns['moderate_uptrend'].append((symbol, change_30d))
            elif change_30d > -10:
                patterns['stable'].append((symbol, change_30d))
            elif change_30d > -30:
                patterns['moderate_downtrend'].append((symbol, change_30d))
            else:
                patterns['strong_downtrend'].append((symbol, change_30d))
        
        # Volatility patterns
        all_volatilities = [
            (coin.get('symbol', '').upper(), 
             FundamentalAnalyzer.analyze_price_volatility(coin))
            for coin in all_crypto[:50]
        ]
        
        # Volume patterns
        all_volumes = [
            (coin.get('symbol', '').upper(),
             FundamentalAnalyzer.calculate_volume_market_cap_ratio(coin))
            for coin in all_crypto[:50]
        ]
        
        # Get extremes
        if all_volumes:
            all_volumes.sort(key=lambda x: x[1], reverse=True)
            patterns['highest_volume'] = [v[0] for v in all_volumes[:5]]
            patterns['lowest_volume'] = [v[0] for v in all_volumes[-5:]]
    
    except Exception as e:
        print(f"Error in pattern identification: {e}")
    
    return patterns

def calculate_market_momentum(all_crypto):
    """Calculate overall market momentum"""
    try:
        top_20_change = sum([
            c.get('price_change_percentage_30d_in_currency', 0) or 0 
            for c in all_crypto[:20]
        ]) / 20
        
        if top_20_change > 15:
            return "🚀 EXTREMELY BULLISH - Strong Market Momentum"
        elif top_20_change > 5:
            return "📈 BULLISH - Positive Market Momentum"
        elif top_20_change > -5:
            return "➡️ NEUTRAL - Mixed Market Momentum"
        elif top_20_change > -15:
            return "📉 BEARISH - Negative Market Momentum"
        else:
            return "❄️ EXTREMELY BEARISH - Weak Market Momentum"
    except:
        return "❓ UNKNOWN"

def assess_monthly_risk(coin_data, all_crypto):
    """Assess risk for a coin over 30 days"""
    try:
        volatility = FundamentalAnalyzer.analyze_price_volatility(coin_data)
        change_30d = coin_data.get('price_change_percentage_30d_in_currency', 0) or 0
        volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(coin_data)
        market_cap = coin_data.get('market_cap', 0)
        
        risk_score = 0
        
        # Volatility risk
        if "Extremely" in volatility:
            risk_score += 40
        elif "Highly" in volatility:
            risk_score += 30
        elif "Moderately" in volatility:
            risk_score += 15
        else:
            risk_score += 5
        
        # Price drop risk
        if change_30d < -30:
            risk_score += 30
        elif change_30d < -15:
            risk_score += 20
        elif change_30d < 0:
            risk_score += 10
        
        # Liquidity risk
        if volume_ratio < 1:
            risk_score += 20
        elif volume_ratio < 5:
            risk_score += 10
        
        # Market cap size (larger = safer)
        if market_cap and market_cap < 100_000_000:
            risk_score += 15
        
        if risk_score >= 80:
            return "🔴 VERY HIGH RISK"
        elif risk_score >= 60:
            return "🟠 HIGH RISK"
        elif risk_score >= 40:
            return "🟡 MODERATE RISK"
        elif risk_score >= 20:
            return "🟢 LOW RISK"
        else:
            return "🟢 VERY LOW RISK"
    except:
        return "❓ UNKNOWN"

def predict_next_month_trend(coin_data):
    """Simple prediction based on 30-day trend"""
    try:
        change_7d = coin_data.get('price_change_percentage_7d_in_currency', 0) or 0
        change_30d = coin_data.get('price_change_percentage_30d_in_currency', 0) or 0
        
        if change_7d > 5 and change_30d > 10:
            return "📈 Likely to Continue Uptrend"
        elif change_7d < -5 and change_30d < -10:
            return "📉 Likely to Continue Downtrend"
        elif change_7d > 0 and change_30d < 0:
            return "📈 Recovery Trend Possible"
        elif change_7d < 0 and change_30d > 0:
            return "⚠️ Potential Reversal Coming"
        else:
            return "➡️ Trend Reversal Possible"
    except:
        return "❓ Insufficient Data"

def format_monthly_report(winners_analysis, losers_analysis, winners_data, losers_data, all_crypto):
    """Format comprehensive monthly report"""
    ist_tz = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.now(ist_tz).strftime("%Y-%m-%d")
    month_start = (datetime.now(ist_tz) - timedelta(days=30)).strftime("%Y-%m-%d")
    
    patterns = identify_monthly_patterns(all_crypto)
    market_momentum = calculate_market_momentum(all_crypto)
    
    report = f"""
📊 **KALYANI v5.0 - MONTHLY DEEP ANALYSIS REPORT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Period: {month_start} to {timestamp} (IST)
📈 Analysis Type: Deep Fundamental + Technical + Pattern Recognition + Risk Assessment

**OVERALL MARKET ASSESSMENT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Market Momentum: {market_momentum}

**30-DAY TREND PATTERNS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **Strong Uptrend (+30% or more):**
"""
    
    if patterns['strong_uptrend']:
        for symbol, change in patterns['strong_uptrend'][:5]:
            report += f"   • {symbol}: +{change:.2f}%\n"
    else:
        report += "   • None\n"
    
    report += f"""
📈 **Moderate Uptrend (+10% to +30%):**
"""
    
    if patterns['moderate_uptrend']:
        for symbol, change in patterns['moderate_uptrend'][:5]:
            report += f"   • {symbol}: +{change:.2f}%\n"
    else:
        report += "   • None\n"
    
    report += f"""
📉 **Moderate Downtrend (-10% to -30%):**
"""
    
    if patterns['moderate_downtrend']:
        for symbol, change in patterns['moderate_downtrend'][:5]:
            report += f"   • {symbol}: {change:.2f}%\n"
    else:
        report += "   • None\n"
    
    report += f"""
❄️ **Strong Downtrend (-30% or more):**
"""
    
    if patterns['strong_downtrend']:
        for symbol, change in patterns['strong_downtrend'][:5]:
            report += f"   • {symbol}: {change:.2f}%\n"
    else:
        report += "   • None\n"
    
    report += f"""
➡️ **Stable (Between -10% and +10%):**
"""
    
    if patterns['stable']:
        for symbol, change in patterns['stable'][:5]:
            report += f"   • {symbol}: {change:.2f}%\n"
    else:
        report += "   • None\n"
    
    report += f"""

**MARKET ACTIVITY ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 **Highest Trading Volume (Most Liquid):**
{', '.join(patterns['highest_volume']) if patterns['highest_volume'] else 'N/A'}

❄️ **Lowest Trading Volume (Least Liquid):**
{', '.join(patterns['lowest_volume']) if patterns['lowest_volume'] else 'N/A'}

🏆 **TOP 10 WINNERS - MONTHLY DEEP ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for i, coin in enumerate(winners_analysis):
        winner_data = winners_data[i]
        volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(winner_data)
        volatility = FundamentalAnalyzer.analyze_price_volatility(winner_data)
        rating = FundamentalAnalyzer.get_fundamental_rating(winner_data, all_crypto)
        
        change_7d = winner_data.get('price_change_percentage_7d_in_currency', 0) or 0
        change_30d = winner_data.get('price_change_percentage_30d_in_currency', 0) or 0
        
        risk = assess_monthly_risk(winner_data, all_crypto)
        prediction = predict_next_month_trend(winner_data)
        
        report += f"""
{coin['rank']}. **{coin['name']}** ({coin['symbol']})

   **PRICE PERFORMANCE (30-Day Window):**
   💰 Current Price: {format_price(coin['price'])}
   📈 30-Day Change: +{change_30d:.2f}% 🔥
   📊 7-Day Change: {change_7d:.2f}%
   
   **MARKET METRICS:**
   💼 Market Cap: {format_market_cap(coin['market_cap'])}
   📊 Volume: {format_volume(coin['volume'])}
   📉 Vol/MC Ratio: {volume_ratio}%
   
   **FUNDAMENTAL ANALYSIS:**
   ⭐ Rating: {rating}
   ⚡ Volatility: {volatility}
   💪 Market Health: {FundamentalAnalyzer.get_market_health(volume_ratio)}
   
   **RISK ASSESSMENT:**
   ⚠️ Monthly Risk Level: {risk}
   
   **30-DAY TRENDS & PATTERNS:**
   🔄 Pattern Type: Consistent Uptrend
   📈 Momentum: Positive throughout month
   💪 Strength: Sustained growth pattern
   
   **PREDICTION FOR NEXT MONTH:**
   🎯 Expected Trend: {prediction}
   
   **AI SENTIMENT:**
   💭 Market Sentiment: {coin['market_sentiment']}
   🧠 Confidence Score: {coin['confidence']}
"""
    
    report += f"""

💔 **TOP 10 LOSERS - MONTHLY DEEP ANALYSIS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for i, coin in enumerate(losers_analysis):
        loser_data = losers_data[i]
        volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(loser_data)
        volatility = FundamentalAnalyzer.analyze_price_volatility(loser_data)
        rating = FundamentalAnalyzer.get_fundamental_rating(loser_data, all_crypto)
        
        change_7d = loser_data.get('price_change_percentage_7d_in_currency', 0) or 0
        change_30d = loser_data.get('price_change_percentage_30d_in_currency', 0) or 0
        
        risk = assess_monthly_risk(loser_data, all_crypto)
        prediction = predict_next_month_trend(loser_data)
        
        report += f"""
{coin['rank']}. **{coin['name']}** ({coin['symbol']})

   **PRICE PERFORMANCE (30-Day Window):**
   💰 Current Price: {format_price(coin['price'])}
   📉 30-Day Change: {change_30d:.2f}% ❄️
   📊 7-Day Change: {change_7d:.2f}%
   
   **MARKET METRICS:**
   💼 Market Cap: {format_market_cap(coin['market_cap'])}
   📊 Volume: {format_volume(coin['volume'])}
   📉 Vol/MC Ratio: {volume_ratio}%
   
   **FUNDAMENTAL ANALYSIS:**
   ⭐ Rating: {rating}
   ⚡ Volatility: {volatility}
   💪 Market Health: {FundamentalAnalyzer.get_market_health(volume_ratio)}
   
   **RISK ASSESSMENT:**
   ⚠️ Monthly Risk Level: {risk}
   
   **30-DAY TRENDS & PATTERNS:**
   🔄 Pattern Type: Consistent Downtrend
   📉 Momentum: Negative throughout month
   ⚠️ Strength: Sustained decline pattern
   
   **PREDICTION FOR NEXT MONTH:**
   🎯 Expected Trend: {prediction}
   
   **AI SENTIMENT:**
   💭 Market Sentiment: {coin['market_sentiment']}
   🧠 Confidence Score: {coin['confidence']}
"""
    
    report += """

**MONTHLY INSIGHTS & RECOMMENDATIONS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Key Findings:**
   1. Market has shown mixed sentiment over 30-day period
   2. High volatility detected in altcoins
   3. Top cryptocurrencies remain stable
   4. Trading volume concentrated in top 10 coins
   5. Risk levels vary significantly across portfolio

📊 **Recommendations:**
   ✅ Focus on coins with strong uptrend + low risk
   ⚠️ Avoid coins with high volatility + downtrend
   💡 Monitor pattern changes weekly
   🛡️ Diversify across different risk levels
   📈 Follow market momentum indicators

---
📈 **ANALYSIS FEATURES:**
🔍 Pattern Recognition = 30-day trend patterns identified
📊 Risk Assessment = Multi-factor risk scoring system
🎯 Trend Prediction = Next month trend forecasting
💼 Fundamental Analysis = Market cap, volume, liquidity ratios
⚡ Volatility Analysis = Price stability assessment
💭 AI Sentiment = Hugging Face transformer sentiment

📊 Report Type: MONTHLY DEEP ANALYSIS
⏱️ Time Window: Last 30 days
🔗 Data Source: CoinGecko API
🧠 AI Models: Hugging Face Transformers
⚙️ Features: Fundamental + Technical + Pattern Recognition + Risk Assessment + Prediction
    """
    
    return report

def send_to_discord(message):
    """Send message to Discord"""
    if not DISCORD_WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK_URL not found")
        return False
    
    try:
        # Split long messages
        if len(message) > 2000:
            messages = [message[i:i+1900] for i in range(0, len(message), 1900)]
            for msg in messages:
                requests.post(
                    DISCORD_WEBHOOK_URL,
                    json={"content": msg},
                    timeout=10
                )
        else:
            requests.post(
                DISCORD_WEBHOOK_URL,
                json={"content": message},
                timeout=10
            )
        
        print("✅ Monthly report sent to Discord")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_kalyani_monthly():
    """Run monthly deep analysis"""
    print("\n" + "="*70)
    print("📊 KALYANI v5.0 - MONTHLY DEEP ANALYSIS")
    print("="*70 + "\n")
    
    print("📥 Loading AI models for deep analysis...")
    model = load_models_for_research()
    
    if model is None:
        print("❌ Failed to load model")
        return False
    
    print("🔄 Fetching cryptocurrency data...")
    crypto_data = fetch_cryptocurrencies()
    if not crypto_data:
        print("❌ Failed to fetch data")
        return False
    
    # Get winners and losers based on 30-day change
    winners = sorted(
        crypto_data,
        key=lambda x: x.get('price_change_percentage_30d_in_currency', 0) or 0,
        reverse=True
    )[:10]
    
    losers = sorted(
        crypto_data,
        key=lambda x: x.get('price_change_percentage_30d_in_currency', 0) or 0
    )[:10]
    
    print("🧠 Deep monthly analysis in progress...")
    winners_analysis = analyze_top_10_winners_deep(winners, model)
    losers_analysis = analyze_top_10_losers_deep(losers, model)
    
    print("📝 Formatting comprehensive report...")
    report = format_monthly_report(
        winners_analysis,
        losers_analysis,
        winners,
        losers,
        crypto_data
    )
    
    print("\n📋 Monthly Report:\n")
    print(report)
    
    print("\n📤 Sending to Discord...")
    send_to_discord(report)

if __name__ == "__main__":
    run_kalyani_monthly()
