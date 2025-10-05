# risk_manager.py
import pandas as pd
from datetime import datetime, timedelta


class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_trades = 0
        self.daily_pnl = 0
        self.last_reset = datetime.now()
        self.open_positions = []
        self.quick_mode = config.get('quick_mode', False)
        self.last_trade_time = {}
        self.cooldown_period = 30  # segundos entre trades no mesmo par

    async def can_trade(self):
        """Verificação rápida de risco"""
        self._reset_daily_counters()

        if self.daily_trades >= self.config['max_daily_trades']:
            return False
        if self.daily_pnl <= self.config['daily_loss_limit']:
            return False

        return True

    async def execute_trade(self, market, signal, trader):
        """Execução com cooldown para evitar trades repetitivos"""
        try:
            symbol = market['symbol']

            # Verifica cooldown
            if symbol in self.last_trade_time:
                time_since_last = (datetime.now() - self.last_trade_time[symbol]).total_seconds()
                if time_since_last < self.cooldown_period:
                    print(f"⏳ Cooldown ativo para {symbol}: {self.cooldown_period - time_since_last:.0f}s restantes")
                    return None

            # Cálculos rápidos
            position_size = self._quick_position_size(market, signal)

            if position_size <= 0:
                return None

            # Ordem de mercado para velocidade
            trade = await trader.place_market_order(
                symbol=symbol,
                side=signal['action'],
                amount=position_size
            )

            if trade:
                self.daily_trades += 1
                self.last_trade_time[symbol] = datetime.now()
                self._set_quick_stops(market, signal, trade)

            return trade

        except Exception as e:
            print(f"❌ Erro execução rápida: {e}")
            return None

    def _quick_position_size(self, market, signal):
        """Cálculo rápido de tamanho de posição"""
        base_size = self.config['max_position_size'] * 0.08  # 8% do máximo

        # Ajusta baseado na confiança
        if signal['confidence'] > 0.7:
            base_size *= 1.3
        elif signal['confidence'] > 0.8:
            base_size *= 1.5

        return min(base_size, self.config['max_position_size'])

    def _set_quick_stops(self, market, signal, trade):
        """Stops simplificados"""
        if signal['action'] == 'buy':
            stop_price = market['current_price'] * 0.992  # -0.8%
            take_profit = market['current_price'] * 1.015  # +1.5%
        else:
            stop_price = market['current_price'] * 1.008  # +0.8%
            take_profit = market['current_price'] * 0.985  # -1.5%

        self.open_positions.append({
            'trade': trade,
            'stop_loss': stop_price,
            'take_profit': take_profit,
            'timestamp': datetime.now()
        })

    def _reset_daily_counters(self):
        """Reset dos contadores diários"""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.daily_trades = 0
            self.daily_pnl = 0
            self.last_reset = now