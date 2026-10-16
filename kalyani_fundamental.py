class FundamentalAnalyzer:
    """Fundamental analysis for cryptocurrencies"""
    
    @staticmethod
    def analyze_market_cap_rank(coin, all_coins):
        """Analyze market cap ranking"""
        try:
            market_cap = coin.get('market_cap', 0)
            
            # Find rank
            ranked = sorted(
                all_coins,
                key=lambda x: x.get('market_cap', 0) or 0,
                reverse=True
            )
            
            for idx, c in enumerate(ranked, 1):
                if c.get('id') == coin.get('id'):
                    return idx
            return "N/A"
        except:
            return "N/A"
    
    @staticmethod
    def calculate_volume_market_cap_ratio(coin):
        """Calculate Volume to Market Cap ratio"""
        try:
            volume = coin.get('total_volume', 0) or 0
            market_cap = coin.get('market_cap', 0) or 0
            
            if market_cap == 0:
                return 0
            
            ratio = (volume / market_cap) * 100
            return round(ratio, 2)
        except:
            return 0
    
    @staticmethod
    def get_market_health(volume_ratio):
        """Determine market health based on volume ratio"""
        if volume_ratio > 20:
            return "🔥 Extremely High Activity"
        elif volume_ratio > 10:
            return "🚀 Very High Activity"
        elif volume_ratio > 5:
            return "📈 High Activity"
        elif volume_ratio > 1:
            return "➡️ Normal Activity"
        else:
            return "❄️ Low Activity"
    
    @staticmethod
    def analyze_price_volatility(coin, historical_changes=None):
        """Analyze price volatility"""
        try:
            change_7d = coin.get('price_change_percentage_7d_in_currency', 0) or 0
            change_30d = coin.get('price_change_percentage_30d_in_currency', 0) or 0
            change_24h = coin.get('price_change_percentage_24h', 0) or 0
            
            avg_volatility = abs((change_7d + change_30d + change_24h) / 3)
            
            if avg_volatility > 20:
                return "⚡ Extremely Volatile"
            elif avg_volatility > 10:
                return "🌪️ Highly Volatile"
            elif avg_volatility > 5:
                return "📊 Moderately Volatile"
            else:
                return "🛡️ Stable"
        except:
            return "❓ Unknown"
    
    @staticmethod
    def analyze_price_change_periods(coin):
        """Analyze price changes across different time periods"""
        analysis = {}
        
        change_24h = coin.get('price_change_percentage_24h', 0) or 0
        change_7d = coin.get('price_change_percentage_7d_in_currency', 0) or 0
        change_30d = coin.get('price_change_percentage_30d_in_currency', 0) or 0
        
        analysis['24h'] = {
            'change': round(change_24h, 2),
            'signal': "📈 UP" if change_24h > 0 else "📉 DOWN"
        }
        
        analysis['7d'] = {
            'change': round(change_7d, 2),
            'signal': "📈 UP" if change_7d > 0 else "📉 DOWN"
        }
        
        analysis['30d'] = {
            'change': round(change_30d, 2),
            'signal': "📈 UP" if change_30d > 0 else "📉 DOWN"
        }
        
        return analysis
    
    @staticmethod
    def identify_patterns(coin_history):
        """Identify repeating patterns in price history"""
        patterns = []
        
        if not coin_history or len(coin_history) < 3:
            return ["📊 Insufficient data for pattern analysis"]
        
        # Check for consistent growth
        changes = [coin_history[i+1] - coin_history[i] for i in range(len(coin_history)-1)]
        
        if all(c > 0 for c in changes):
            patterns.append("📈 Consistent Uptrend")
        elif all(c < 0 for c in changes):
            patterns.append("📉 Consistent Downtrend")
        elif len([c for c in changes if c > 0]) > len(changes) * 0.6:
            patterns.append("📈 Mostly Uptrend")
        elif len([c for c in changes if c < 0]) > len(changes) * 0.6:
            patterns.append("📉 Mostly Downtrend")
        
        # Check for volatility pattern
        volatility = max(changes) - min(changes)
        if volatility > abs(sum(changes) / len(changes)) * 2:
            patterns.append("🌊 High Volatility Pattern")
        
        # Check for recovery pattern
        if changes[-1] > 0 and sum(changes[-3:]) > 0:
            patterns.append("💪 Recovery Pattern")
        
        return patterns if patterns else ["➡️ No Clear Pattern"]
    
    @staticmethod
    def get_fundamental_rating(coin, all_coins):
        """Get overall fundamental rating"""
        try:
            volume_ratio = FundamentalAnalyzer.calculate_volume_market_cap_ratio(coin)
            rank = FundamentalAnalyzer.analyze_market_cap_rank(coin, all_coins)
            volatility = FundamentalAnalyzer.analyze_price_volatility(coin)
            
            score = 0
            
            # Market cap rank (lower is better)
            if isinstance(rank, int) and rank <= 100:
                score += 25
            elif isinstance(rank, int) and rank <= 500:
                score += 15
            
            # Volume ratio (higher is better)
            if volume_ratio > 10:
                score += 25
            elif volume_ratio > 5:
                score += 15
            
            # Stability (lower volatility is better for safety)
            if "Stable" in volatility:
                score += 25
            elif "Moderate" in volatility:
                score += 15
            
            if score >= 60:
                return "⭐⭐⭐ STRONG"
            elif score >= 40:
                return "⭐⭐ MODERATE"
            else:
                return "⭐ WEAK"
        except:
            return "❓ UNKNOWN"
