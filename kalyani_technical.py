import pandas as pd
import numpy as np
from scipy import stats

class TechnicalAnalyzer:
    """Technical analysis for cryptocurrencies"""
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate Relative Strength Index"""
        if len(prices) < period:
            return 50  # Neutral
        
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        
        rsi = 100 - (100 / (1 + rs)) if rs else 50
        return round(rsi, 2)
    
    @staticmethod
    def calculate_macd(prices):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < 26:
            return None, None, None
        
        ema_12 = pd.Series(prices).ewm(span=12).mean().iloc[-1]
        ema_26 = pd.Series(prices).ewm(span=26).mean().iloc[-1]
        macd = ema_12 - ema_26
        
        return round(macd, 4), "📈 BULLISH" if macd > 0 else "📉 BEARISH"
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20):
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None, None, None
        
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        
        current_price = prices[-1]
        
        if current_price > upper:
            signal = "⬆️ OVERBOUGHT"
        elif current_price < lower:
            signal = "⬇️ OVERSOLD"
        else:
            signal = "➡️ NORMAL"
        
        return round(upper, 2), round(lower, 2), signal
    
    @staticmethod
    def calculate_momentum(prices, period=10):
        """Calculate Price Momentum"""
        if len(prices) < period:
            return 0
        
        momentum = ((prices[-1] - prices[-period]) / prices[-period]) * 100
        return round(momentum, 2)
    
    @staticmethod
    def detect_support_resistance(prices):
        """Detect support and resistance levels"""
        if len(prices) < 10:
            return None, None
        
        recent_prices = prices[-20:]
        support = min(recent_prices)
        resistance = max(recent_prices)
        
        return round(support, 6), round(resistance, 6)
    
    @staticmethod
    def calculate_trend(prices):
        """Determine trend direction"""
        if len(prices) < 5:
            return "❓ UNKNOWN"
        
        recent = prices[-5:]
        if recent[-1] > recent[0]:
            if recent[-1] > max(recent[:-1]):
                return "🔥 STRONG UPTREND"
            else:
                return "📈 UPTREND"
        else:
            if recent[-1] < min(recent[:-1]):
                return "❄️ STRONG DOWNTREND"
            else:
                return "📉 DOWNTREND"
    
    @staticmethod
    def get_technical_signals(price_change, rsi, momentum):
        """Get combined technical signals"""
        signals = []
        
        # RSI signals
        if rsi > 70:
            signals.append("⚠️ RSI Overbought")
        elif rsi < 30:
            signals.append("💡 RSI Oversold")
        
        # Momentum signals
        if momentum > 10:
            signals.append("🚀 Strong Momentum Up")
        elif momentum < -10:
            signals.append("⚠️ Strong Momentum Down")
        
        return signals if signals else ["➡️ No Strong Signals"]
