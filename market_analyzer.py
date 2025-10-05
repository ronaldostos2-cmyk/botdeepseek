# market_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime


class MarketFilter:
    def __init__(self, config):
        self.config = config
        self.last_update = {}

    async def get_filtered_markets(self):
        """Retorna mercados com dados variáveis"""
        all_markets = [
            {'symbol': 'BTC/USDT', 'volume_24h': 25000000, 'spread': 0.0002, 'base_price': 45000},
            {'symbol': 'ETH/USDT', 'volume_24h': 15000000, 'spread': 0.0005, 'base_price': 3000},
            {'symbol': 'ADA/USDT', 'volume_24h': 500000, 'spread': 0.001, 'base_price': 0.45},
            {'symbol': 'BNB/USDT', 'volume_24h': 8000000, 'spread': 0.0003, 'base_price': 350},
            {'symbol': 'SOL/USDT', 'volume_24h': 12000000, 'spread': 0.0006, 'base_price': 120},
        ]

        filtered = []
        for market in all_markets:
            if self._passes_filters(market):
                # Gera dados OHLCV com variação temporal
                ohlcv_data = self._generate_dynamic_ohlcv(market)
                market['ohlcv'] = ohlcv_data
                market['current_price'] = ohlcv_data['close'].iloc[-1]
                filtered.append(market)

        return filtered

    def _passes_filters(self, market):
        """Aplica filtros ao mercado"""
        if market['volume_24h'] < self.config.get('min_volume_24h', 1000000):
            return False
        if market['spread'] > self.config.get('max_spread', 0.001):
            return False
        allowed_pairs = self.config.get('allowed_pairs', [])
        if allowed_pairs and market['symbol'] not in allowed_pairs:
            return False
        return True

    def _generate_dynamic_ohlcv(self, market):
        """Gera dados OHLCV que variam com o tempo"""
        base_price = market['base_price']
        seed = hash(market['symbol']) % 1000 + int(datetime.now().timestamp() // 60)
        np.random.seed(seed)

        # Gera 50 períodos de dados
        dates = pd.date_range(end=pd.Timestamp.now(), periods=50, freq='1min')

        # Simula preços com tendência e volatilidade realista
        prices = [base_price]
        for i in range(1, 50):
            # Volatilidade baseada no ativo + variação temporal
            time_factor = 1 + (i / 50) * 0.1  # Pequena tendência temporal
            volatility = 0.008 if 'BTC' in market['symbol'] else 0.012
            returns = np.random.normal(0.0002 * time_factor, volatility)
            new_price = max(0.01, prices[-1] * (1 + returns))
            prices.append(new_price)

        prices = np.array(prices)

        # Cria DataFrame OHLCV
        df = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': prices * (1 + np.abs(np.random.normal(0.01, 0.004, 50))),
            'low': prices * (1 - np.abs(np.random.normal(0.01, 0.004, 50))),
            'close': prices * (1 + np.random.normal(0, 0.005, 50)),
            'volume': np.random.lognormal(10, 1.2, 50) * 1000
        })

        # Garante consistência
        df['high'] = df[['open', 'close', 'high']].max(axis=1)
        df['low'] = df[['open', 'close', 'low']].min(axis=1)
        df['close'] = np.clip(df['close'], df['low'], df['high'])

        return df