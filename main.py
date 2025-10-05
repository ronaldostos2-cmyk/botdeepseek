# main.py
import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from exchange_trader import Trader
from risk_manager import RiskManager
from trading_strategy import TradingStrategy
from market_analyzer import MarketFilter
from logger import setup_logging


class TradingBot:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.trader = Trader(config['exchange'])
        self.risk_manager = RiskManager(config['risk_management'])
        self.strategy = TradingStrategy(config['strategy'])
        self.market_filter = MarketFilter(config['filters'])
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        setup_logging()
        self.logger = logging.getLogger(__name__)

        # Cache para evitar reanálises desnecessárias
        self.last_analysis = {}
        self.analysis_cache_ttl = 3  # segundos

    async def run(self):
        """Execução principal otimizada"""
        self.running = True
        print("🚀 Bot de Trading RÁPIDO iniciado")
        print("⚡ Modo: Análise paralela e entradas aceleradas")

        cycle_count = 0

        try:
            while self.running:
                cycle_count += 1
                start_time = time.time()

                print(f"\n🎯 Ciclo {cycle_count} - Buscando oportunidades...")

                # 1. Busca mercados em paralelo
                markets = await self.market_filter.get_filtered_markets()
                if not markets:
                    print("   ⚠️ Nenhum mercado passou nos filtros")
                    await asyncio.sleep(1)
                    continue

                print(f"   📊 {len(markets)} mercados para análise")

                # 2. Analisa mercados em paralelo
                analysis_tasks = []
                for market in markets:
                    # Verifica cache para evitar reanálise
                    cache_key = f"{market['symbol']}_{int(time.time() // self.analysis_cache_ttl)}"
                    if cache_key not in self.last_analysis:
                        task = asyncio.create_task(self.analyze_market(market))
                        analysis_tasks.append((market['symbol'], task))
                    else:
                        print(f"   ♻️ {market['symbol']} usando cache")

                # Aguarda todas as análises paralelas
                signals = []
                for symbol, task in analysis_tasks:
                    try:
                        signal = await task
                        signals.append(signal)
                    except Exception as e:
                        print(f"   ❌ Erro análise {symbol}: {e}")
                        signals.append({'action': 'hold', 'confidence': 0})

                # 3. Executa trades para sinais válidos
                trade_count = 0
                for i, signal in enumerate(signals):
                    if (isinstance(signal, dict) and
                            signal.get('action') != 'hold' and
                            signal.get('confidence', 0) >= self.config['strategy']['min_confidence']):

                        market = markets[i]
                        print(
                            f"   🎯 SINAL FORTE: {market['symbol']} {signal['action']} (conf: {signal['confidence']:.2f})")

                        trade_result = await self.execute_trade_if_approved(market, signal)
                        if trade_result:
                            trade_count += 1

                # 4. Timing otimizado
                processing_time = time.time() - start_time
                sleep_time = max(0.1, self.config['scan_interval'] - processing_time)

                print(f"   ⏱️ Processamento: {processing_time:.2f}s | Trades: {trade_count} | Sleep: {sleep_time:.1f}s")

                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

        except Exception as e:
            print(f"❌ Erro no bot: {e}")
            self.logger.error(f"Erro no bot: {e}")

    async def analyze_market(self, market):
        """Analisa um mercado individualmente"""
        try:
            # Cache para evitar análise repetida
            cache_key = f"{market['symbol']}_{int(time.time() // self.analysis_cache_ttl)}"

            if cache_key in self.last_analysis:
                return self.last_analysis[cache_key]

            signal = await self.strategy.analyze(market)
            self.last_analysis[cache_key] = signal

            # Limpa cache antigo
            current_time_key = int(time.time() // self.analysis_cache_ttl)
            self.last_analysis = {k: v for k, v in self.last_analysis.items()
                                  if int(k.split('_')[-1]) >= current_time_key - 1}

            return signal

        except Exception as e:
            print(f"❌ Erro analisando {market['symbol']}: {e}")
            return {'action': 'hold', 'confidence': 0}

    async def execute_trade_if_approved(self, market, signal):
        """Executa trade se aprovado pelo risk manager"""
        if await self.risk_manager.can_trade():
            trade_result = await self.risk_manager.execute_trade(market, signal, self.trader)
            if trade_result:
                print(f"   ✅ TRADE EXECUTADO: {market['symbol']} {signal['action']}")
                return trade_result
        else:
            print(f"   ⚠️ Trade bloqueado pelo gerenciamento de risco")
        return None

    def stop(self):
        """Para o bot"""
        self.running = False
        self.thread_pool.shutdown()
        print("🛑 Bot parado")


# ⚡ CONFIGURAÇÃO OTIMIZADA PARA VELOCIDADE
CONFIG = {
    'exchange': {
        'name': 'binance',
        'api_key': 'd47789171a725c0b7becb283a989f44963698d6349a857a33d6e56750823f364',
        'secret': 'b217fe9799c0fa744c7c9703d3f6b55b09ef7c92c927cb25d8b2e890c73dbcce',
        'testnet': True
    },
    'risk_management': {
        'max_daily_trades': 20,
        'max_position_size': 500,
        'daily_loss_limit': -300,
        'risk_per_trade': 0.01,
        'quick_mode': True
    },
    'strategy': {
        'rsi_period': 9,
        'rsi_overbought': 75,
        'rsi_oversold': 25,
        'ema_fast': 5,
        'ema_slow': 12,
        'min_confidence': 0.55,
        'timeframe': '1m'
    },
    'filters': {
        'min_volume_24h': 500000,
        'max_spread': 0.001,
        'allowed_pairs': ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'BNB/USDT', 'SOL/USDT'],
        'exclude_stablecoins': True
    },
    'scan_interval': 3
}


async def main():
    print("🚀 INICIANDO BOT DE ALTA VELOCIDADE")
    print("⚡ Configuração Otimizada:")
    print(f"   • Scan Interval: {CONFIG['scan_interval']}s")
    print(f"   • EMAs: {CONFIG['strategy']['ema_fast']}/{CONFIG['strategy']['ema_slow']}")
    print(f"   • RSI: {CONFIG['strategy']['rsi_period']} períodos")
    print(f"   • Pares: {len(CONFIG['filters']['allowed_pairs'])} ativos")
    print(f"   • Modo: Paralelização ativa")

    bot = TradingBot(CONFIG)
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Parando bot...")
        bot.stop()


if __name__ == "__main__":
    asyncio.run(main())