# trading_strategy.py
import pandas as pd
import numpy as np
from technical_indicators import calculate_rsi_fast, calculate_ema_fast


class TradingStrategy:
    def __init__(self, config):
        self.config = config
        self.rsi_period = config.get('rsi_period', 9)
        self.rsi_overbought = config.get('rsi_overbought', 75)
        self.rsi_oversold = config.get('rsi_oversold', 25)
        self.ema_fast = config.get('ema_fast', 5)
        self.ema_slow = config.get('ema_slow', 12)
        self.min_confidence = config.get('min_confidence', 0.55)
        self.timeframe = config.get('timeframe', '1m')

        # Contador para variar sinais
        self.cycle_count = 0

    async def analyze(self, market_data):
        """Análise otimizada para velocidade SEM WARNINGS"""
        try:
            self.cycle_count += 1

            # Cria cópia segura dos dados
            df = market_data['ohlcv'].copy()

            # Usa menos dados para análise mais rápida
            if len(df) > 30:
                df = df.tail(30).copy()

            # Garante que temos dados suficientes
            if len(df) < 15:
                return {'action': 'hold', 'confidence': 0}

            # Garante que os preços são floats
            close_prices = df['close'].astype(float).values

            # Calcula indicadores com proteção
            rsi_values = calculate_rsi_fast(close_prices, self.rsi_period)
            ema_fast_values = calculate_ema_fast(close_prices, self.ema_fast)
            ema_slow_values = calculate_ema_fast(close_prices, self.ema_slow)

            # Atualiza DataFrame de forma segura
            df = df.assign(
                rsi=rsi_values,
                ema_fast=ema_fast_values,
                ema_slow=ema_slow_values
            )

            latest = df.iloc[-1]

            # Estratégia com variação para evitar trades repetitivos
            signal = self._dynamic_signal(latest, df, market_data['symbol'])
            return signal

        except Exception as e:
            print(f"❌ Erro análise {market_data.get('symbol', 'unknown')}: {e}")
            return {'action': 'hold', 'confidence': 0}

    def _dynamic_signal(self, latest, df, symbol):
        """Sinal dinâmico que varia para evitar repetição"""
        signal = {'action': 'hold', 'confidence': 0, 'indicators': {}}

        # Verifica se os indicadores são válidos
        if (np.isnan(latest['rsi']) or np.isnan(latest['ema_fast']) or
                np.isnan(latest['ema_slow'])):
            return signal

        # 1. Condição RSI com filtro de qualidade
        rsi_condition = 0
        rsi_value = latest['rsi']
        if 20 <= rsi_value <= self.rsi_oversold:
            rsi_condition = 1
        elif self.rsi_overbought <= rsi_value <= 80:
            rsi_condition = -1

        # 2. Condição EMA com confirmação
        ema_condition = 0
        price_vs_fast = latest['close'] / latest['ema_fast']
        price_vs_slow = latest['close'] / latest['ema_slow']

        if price_vs_fast > 1.002 and price_vs_slow > 1.001:  # Preço acima das EMAs
            ema_condition = 1
        elif price_vs_fast < 0.998 and price_vs_slow < 0.999:  # Preço abaixo das EMAs
            ema_condition = -1

        # 3. Condição de momentum
        momentum_condition = 0
        if len(df) >= 5:
            price_change = (latest['close'] / df['close'].iloc[-5] - 1) * 100
            if price_change > 0.5:  # +0.5% nos últimos 5 períodos
                momentum_condition = 1
            elif price_change < -0.5:  # -0.5% nos últimos 5 períodos
                momentum_condition = -1

        # 4. Variação baseada no ciclo para evitar repetição
        cycle_variation = (self.cycle_count + hash(symbol) % 10) % 3 - 1

        # Sinal combinado
        total_score = rsi_condition + ema_condition + momentum_condition + cycle_variation

        # Aplica filtros de qualidade
        min_rsi_quality = abs(rsi_value - 50) > 10  # RSI distante de 50
        ema_spread = abs(latest['ema_fast'] - latest['ema_slow']) / latest['ema_slow'] > 0.002

        if total_score >= 2 and min_rsi_quality and ema_spread:
            signal['action'] = 'buy'
            signal['confidence'] = min(0.85, 0.5 + (total_score * 0.1))
        elif total_score <= -2 and min_rsi_quality and ema_spread:
            signal['action'] = 'sell'
            signal['confidence'] = min(0.85, 0.5 + (abs(total_score) * 0.1))

        signal['indicators'] = {
            'rsi': float(rsi_value),
            'ema_fast': float(latest['ema_fast']),
            'ema_slow': float(latest['ema_slow']),
            'score': total_score,
            'price_change': price_change if len(df) >= 5 else 0
        }

        return signal