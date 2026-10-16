import torch
from transformers import pipeline
import pandas as pd

# Model selection
MODELS_SELECTION = {
    'hourly': {
        'sentiment': 'distilbert-base-uncased-finetuned-sst-2-english'
    },
    'research': {
        'sentiment': 'ProsusAI/finbert',
        'market': 'facebook/bart-large-mnli',
        'summarizer': 'facebook/bart-large-cnn',
    }
}

def load_models_for_hourly():
    """Load fast models for hourly analysis"""
    print("Loading hourly models...")
    try:
        sentiment_model = pipeline(
            "sentiment-analysis",
            model=MODELS_SELECTION['hourly']['sentiment'],
            device=0 if torch.cuda.is_available() else -1
        )
        print("✅ Hourly models loaded successfully")
        return sentiment_model
    except Exception as e:
        print(f"❌ Error loading hourly models: {e}")
        return None

def load_models_for_research():
    """Load detailed models for deep research"""
    print("Loading research models...")
    try:
        sentiment_model = pipeline(
            "sentiment-analysis",
            model=MODELS_SELECTION['research']['sentiment'],
            device=0 if torch.cuda.is_available() else -1
        )
        print("✅ Research models loaded successfully")
        return sentiment_model
    except Exception as e:
        print(f"❌ Error loading research models: {e}")
        return None

def analyze_sentiment_quick(text, model):
    """Quick sentiment analysis for hourly reports"""
    if not text or model is None:
        return {"label": "NEUTRAL", "score": 0.5}
    
    try:
        # Limit text length for speed
        text = text[:512]
        result = model(text, truncation=True)[0]
        return {
            "label": result['label'],
            "score": round(result['score'], 3)
        }
    except Exception as e:
        print(f"Error in quick sentiment analysis: {e}")
        return {"label": "NEUTRAL", "score": 0.5}

def analyze_sentiment_deep(text, model):
    """Deep sentiment analysis for research"""
    if not text or model is None:
        return {"label": "NEUTRAL", "score": 0.5}
    
    try:
        text = text[:512]
        result = model(text, truncation=True)[0]
        return {
            "label": result['label'],
            "score": round(result['score'], 3)
        }
    except Exception as e:
        print(f"Error in deep sentiment analysis: {e}")
        return {"label": "NEUTRAL", "score": 0.5}

def classify_market_sentiment(price_change, sentiment_score):
    """Classify overall market sentiment"""
    if price_change > 5 and sentiment_score > 0.6:
        return "🔥 VERY BULLISH"
    elif price_change > 0 and sentiment_score > 0.5:
        return "📈 BULLISH"
    elif price_change < -5 and sentiment_score < 0.4:
        return "❄️ VERY BEARISH"
    elif price_change < 0 and sentiment_score < 0.5:
        return "📉 BEARISH"
    else:
        return "➡️ NEUTRAL"

def analyze_top_10_winners_quick(winners, model):
    """Analyze all 10 winners quickly"""
    analysis = []
    for idx, coin in enumerate(winners, 1):
        try:
            name = coin.get('name', 'Unknown')
            symbol = coin.get('symbol', '').upper()
            change = coin.get('price_change_percentage_24h', 0)
            price = coin.get('current_price', 0)
            
            # Analyze using model
            text = f"{name} price increased by {change}% in 24 hours"
            sentiment = analyze_sentiment_quick(text, model)
            
            market_sentiment = classify_market_sentiment(change, sentiment['score'])
            
            analysis.append({
                'rank': idx,
                'name': name,
                'symbol': symbol,
                'price': price,
                'change_24h': round(change, 2),
                'sentiment': sentiment['label'],
                'confidence': sentiment['score'],
                'market_sentiment': market_sentiment
            })
        except Exception as e:
            print(f"Error analyzing winner {idx}: {e}")
            continue
    
    return analysis

def analyze_top_10_winners_deep(winners, model):
    """Deep analysis of all 10 winners"""
    analysis = []
    for idx, coin in enumerate(winners, 1):
        try:
            name = coin.get('name', 'Unknown')
            symbol = coin.get('symbol', '').upper()
            change = coin.get('price_change_percentage_24h', 0)
            price = coin.get('current_price', 0)
            market_cap = coin.get('market_cap', 0)
            volume = coin.get('total_volume', 0)
            
            # Deep sentiment analysis
            text = f"{name} cryptocurrency surge with {change}% gain, market cap {market_cap}"
            sentiment = analyze_sentiment_deep(text, model)
            
            market_sentiment = classify_market_sentiment(change, sentiment['score'])
            
            analysis.append({
                'rank': idx,
                'name': name,
                'symbol': symbol,
                'price': price,
                'change_24h': round(change, 2),
                'market_cap': market_cap,
                'volume': volume,
                'sentiment': sentiment['label'],
                'confidence': sentiment['score'],
                'market_sentiment': market_sentiment
            })
        except Exception as e:
            print(f"Error in deep analysis of winner {idx}: {e}")
            continue
    
    return analysis

def analyze_top_10_losers_quick(losers, model):
    """Analyze all 10 losers quickly"""
    analysis = []
    for idx, coin in enumerate(losers, 1):
        try:
            name = coin.get('name', 'Unknown')
            symbol = coin.get('symbol', '').upper()
            change = coin.get('price_change_percentage_24h', 0)
            price = coin.get('current_price', 0)
            
            # Analyze using model
            text = f"{name} price decreased by {abs(change)}% in 24 hours"
            sentiment = analyze_sentiment_quick(text, model)
            
            market_sentiment = classify_market_sentiment(change, sentiment['score'])
            
            analysis.append({
                'rank': idx,
                'name': name,
                'symbol': symbol,
                'price': price,
                'change_24h': round(change, 2),
                'sentiment': sentiment['label'],
                'confidence': sentiment['score'],
                'market_sentiment': market_sentiment
            })
        except Exception as e:
            print(f"Error analyzing loser {idx}: {e}")
            continue
    
    return analysis

def analyze_top_10_losers_deep(losers, model):
    """Deep analysis of all 10 losers"""
    analysis = []
    for idx, coin in enumerate(losers, 1):
        try:
            name = coin.get('name', 'Unknown')
            symbol = coin.get('symbol', '').upper()
            change = coin.get('price_change_percentage_24h', 0)
            price = coin.get('current_price', 0)
            market_cap = coin.get('market_cap', 0)
            volume = coin.get('total_volume', 0)
            
            # Deep sentiment analysis
            text = f"{name} cryptocurrency decline with {abs(change)}% loss, market cap {market_cap}"
            sentiment = analyze_sentiment_deep(text, model)
            
            market_sentiment = classify_market_sentiment(change, sentiment['score'])
            
            analysis.append({
                'rank': idx,
                'name': name,
                'symbol': symbol,
                'price': price,
                'change_24h': round(change, 2),
                'market_cap': market_cap,
                'volume': volume,
                'sentiment': sentiment['label'],
                'confidence': sentiment['score'],
                'market_sentiment': market_sentiment
            })
        except Exception as e:
            print(f"Error in deep analysis of loser {idx}: {e}")
            continue
    
    return analysis
