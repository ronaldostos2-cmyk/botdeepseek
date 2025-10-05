# technical_indicators.py
import pandas as pd
import numpy as np


def calculate_rsi_fast(prices, period=14):
    """RSI otimizado para arrays numpy - SEM WARNINGS"""
    try:
        if len(prices) < period:
            return np.full(len(prices), 50.0)

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        # Calcula médias móveis
        avg_gains = np.zeros_like(prices, dtype=float)
        avg_losses = np.zeros_like(prices, dtype=float)

        # Primeiros valores
        avg_gains[period] = np.mean(gains[:period])
        avg_losses[period] = np.mean(losses[:period])

        # Evita divisão por zero - CORREÇÃO AQUI
        if avg_losses[period] == 0:
            avg_losses[period] = 1e-10  # Valor muito pequeno

        # Restante dos valores
        for i in range(period + 1, len(prices)):
            avg_gains[i] = (avg_gains[i - 1] * (period - 1) + gains[i - 1]) / period
            avg_losses[i] = (avg_losses[i - 1] * (period - 1) + losses[i - 1]) / period

            # Evita divisão por zero - CORREÇÃO AQUI
            if avg_losses[i] == 0:
                avg_losses[i] = 1e-10

        # Calcula RSI com proteção contra divisão por zero
        rs = np.divide(avg_gains, avg_losses, out=np.ones_like(avg_gains), where=avg_losses != 0)
        rsi = 100.0 - (100.0 / (1.0 + rs))

        # Preenche os primeiros valores
        rsi[:period] = 50.0

        # Garante valores válidos
        rsi = np.clip(rsi, 0, 100)
        rsi = np.nan_to_num(rsi, nan=50.0)

        return rsi
    except Exception as e:
        print(f"⚠️ Erro no RSI rápido: {e}")
        return np.full(len(prices), 50.0)


def calculate_ema_fast(prices, period):
    """EMA otimizado para arrays numpy"""
    try:
        ema = np.zeros_like(prices, dtype=float)
        ema[0] = prices[0]
        alpha = 2.0 / (period + 1.0)

        for i in range(1, len(prices)):
            ema[i] = alpha * prices[i] + (1 - alpha) * ema[i - 1]

        return ema
    except Exception as e:
        print(f"⚠️ Erro no EMA rápido: {e}")
        return prices.astype(float) if isinstance(prices, np.ndarray) else np.array(prices, dtype=float)


def calculate_rsi(prices, period=14):
    """RSI usando pandas - SEM WARNINGS"""
    try:
        if len(prices) < period:
            return pd.Series([50] * len(prices), index=prices.index)

        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Evita divisão por zero
        rs = gain / loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))

        return rsi.fillna(50).clip(0, 100)
    except Exception as e:
        print(f"⚠️ Erro no RSI pandas: {e}")
        return pd.Series([50] * len(prices), index=prices.index)


def calculate_ema(prices, period):
    """EMA usando pandas"""
    try:
        return prices.ewm(span=period, adjust=False).mean()
    except Exception as e:
        print(f"⚠️ Erro no EMA pandas: {e}")
        return prices


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """MACD usando pandas"""
    try:
        ema_fast = calculate_ema(prices, fast)
        ema_slow = calculate_ema(prices, slow)
        macd = ema_fast - ema_slow
        macd_signal = calculate_ema(macd, signal)
        return macd, macd_signal
    except Exception as e:
        print(f"⚠️ Erro no MACD: {e}")
        zeros = pd.Series([0] * len(prices), index=prices.index)
        return zeros, zeros


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calcula Bollinger Bands"""
    try:
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    except Exception as e:
        print(f"⚠️ Erro nas Bollinger Bands: {e}")
        return prices, prices, prices