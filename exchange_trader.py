# exchange_trader.py
import pandas as pd
import numpy as np  # 👈 ADICIONAR ESTA LINHA
import asyncio


class Trader:
    def __init__(self, exchange_config):
        self.exchange_config = exchange_config

    async def place_order(self, symbol, side, amount, price):
        """Executa ordem na exchange"""
        try:
            print(f"📊 Ordem: {side} {amount:.6f} {symbol} @ {price:.6f}")

            return {
                'id': f"order_{hash(str((symbol, side, amount, price)))}",
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'timestamp': pd.Timestamp.now(),
                'status': 'filled'
            }

        except Exception as e:
            print(f"❌ Erro executando ordem: {e}")
            return None

    async def place_market_order(self, symbol, side, amount):
        """Ordem de mercado para execução mais rápida"""
        try:
            # Simula preço de mercado atual
            current_price = await self.get_current_price(symbol)

            print(f"⚡ ORDEM MERCADO: {side} {amount:.6f} {symbol} @ ~{current_price:.6f}")

            return {
                'id': f"market_order_{hash(str((symbol, side, amount)))}",
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': current_price,
                'timestamp': pd.Timestamp.now(),
                'status': 'filled',
                'type': 'market'
            }

        except Exception as e:
            print(f"❌ Erro ordem mercado: {e}")
            return None

    async def get_current_price(self, symbol):
        """Obtém preço atual (simulado)"""
        # Preços base para simulação
        price_map = {
            'BTC/USDT': 45000 + (np.random.random() - 0.5) * 1000,
            'ETH/USDT': 3000 + (np.random.random() - 0.5) * 100,
            'ADA/USDT': 0.45 + (np.random.random() - 0.5) * 0.05,
            'BNB/USDT': 350 + (np.random.random() - 0.5) * 10,
            'SOL/USDT': 120 + (np.random.random() - 0.5) * 5,
        }
        return price_map.get(symbol, 100 + (np.random.random() - 0.5) * 10)

    async def get_account_balance(self):
        """Obtém saldo da conta"""
        return {'USDT': 10000, 'BTC': 0.1, 'ETH': 2.5}

    async def cancel_order(self, order_id):
        """Cancela ordem"""
        print(f"❌ Cancelando ordem: {order_id}")
        return True