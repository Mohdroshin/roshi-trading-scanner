import pandas as pd
import yfinance as yf
import requests
import time
import schedule
import os
from datetime import datetime, time as dt_time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("🚀 ROSHI PROFESSIONAL SCANNER - Optimized Profit Targets")
print("🎯 Multiple Breakout Points | 💰 Higher Profit Margins")

class RoshiProfessionalScanner:
    def __init__(self):
        self.brokerage = 40
        self.min_profit = 80  # Increased minimum profit
        
        # PROFESSIONAL PROFIT TARGETS WITH MULTIPLE BREAKOUT POINTS
        self.strategies = {
            'SCALPING': {
                'targets': [1.0, 1.8],  # Two profit targets
                'sl': 0.5, 
                'hold': '5-15min',
                'risk_reward': 2.0
            },
            'INTRADAY': {
                'targets': [2.0, 3.5],  # Conservative + Aggressive targets
                'sl': 0.8,
                'hold': '15min-EOD', 
                'risk_reward': 2.5
            },
            'SWING': {
                'targets': [4.0, 6.0],  # Two swing targets
                'sl': 1.8,
                'hold': '1-3 days',
                'risk_reward': 2.2
            },
            'BREAKOUT': {
                'targets': [3.0, 5.0, 7.0],  # THREE breakout points!
                'sl': 1.2,
                'hold': 'Intraday to Swing',
                'risk_reward': 2.5
            }
        }
        
        # CURATED HIGH-MOMENTUM STOCKS
        self.stocks = {
            'NIFTY50': '^NSEI',
            'BANKNIFTY': '^NSEBANK',
            
            # High Momentum Stocks (institutional favorites)
            'RELIANCE': 'RELIANCE.NS',    # Energy giant, high volatility
            'TCS': 'TCS.NS',              # IT major, consistent moves
            'HDFCBANK': 'HDFCBANK.NS',    # Bank heavyweight
            'ICICIBANK': 'ICICIBANK.NS',  # High beta bank
            'INFY': 'INFY.NS',            # IT momentum
            'BHARTIARTL': 'BHARTIARTL.NS', # Telecom, gap moves
            'SBIN': 'SBIN.NS',            # PSU bank momentum
            'KOTAKBANK': 'KOTAKBANK.NS',  # Private bank moves
            'AXISBANK': 'AXISBANK.NS',    # Banking sector leader
            'MARUTI': 'MARUTI.NS',        # Auto sector bellwether
            'TITAN': 'TITAN.NS',          # Consumer discretionary
            'BAJFINANCE': 'BAJFINANCE.NS', # NBFC momentum
            'TATAMOTORS': 'TATAMOTORS.NS', # Auto, high volume
            'ADANIPORTS': 'ADANIPORTS.NS'  # Infrastructure momentum
        }
        
        self.sent_alerts = {}
    
    def get_professional_data(self, symbol):
        """Get multi-timeframe data for better analysis"""
        try:
            data_15m = yf.Ticker(symbol).history(period='3d', interval='15m')
            data_1h = yf.Ticker(symbol).history(period='1mo', interval='1h')
            return {'15m': data_15m, '1h': data_1h}
        except Exception as e:
            logger.error(f"Data error for {symbol}: {e}")
            return None
    
    def calculate_advanced_levels(self, data):
        """Calculate professional support/resistance with volume analysis"""
        if data is None or data['15m'].empty:
            return None
            
        df_15m = data['15m']
        if len(df_15m) < 20:
            return None
            
        current = df_15m.iloc[-1]
        current_price = current['Close']
        
        # Advanced Support/Resistance
        support = df_15m['Low'].tail(20).min()
        resistance = df_15m['High'].tail(20).max()
        
        # Volume analysis
        avg_volume = df_15m['Volume'].tail(20).mean()
        current_volume = current['Volume']
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Trend analysis
        ma_20 = df_15m['Close'].tail(20).mean()
        ma_50 = df_15m['Close'].tail(50).mean()
        trend = "BULLISH" if ma_20 > ma_50 else "BEARISH"
        
        # Volatility (for position sizing)
        recent_high = df_15m['High'].tail(10).max()
        recent_low = df_15m['Low'].tail(10).min()
        volatility_pct = ((recent_high - recent_low) / current_price) * 100
        
        return {
            'current_price': current_price,
            'support': support,
            'resistance': resistance,
            'volume_ratio': volume_ratio,
            'trend': trend,
            'ma_20': ma_20,
            'ma_50': ma_50,
            'volatility_pct': volatility_pct
        }
    
    def generate_advanced_signals(self, stock_name, levels):
        """Generate professional signals with multiple profit targets"""
        if not levels:
            return []
            
        signals = []
        cp = levels['current_price']
        
        # STRATEGY 1: BREAKOUT WITH MULTIPLE TARGETS (Professional)
        if (cp >= levels['resistance'] and 
            levels['volume_ratio'] > 1.8 and
            levels['trend'] == 'BULLISH'):
            
            # Calculate multiple targets
            targets = [cp * (1 + target_pct/100) for target_pct in self.strategies['BREAKOUT']['targets']]
            sl = cp * (1 - self.strategies['BREAKOUT']['sl']/100)
            
            signals.append({
                'strategy': 'BREAKOUT',
                'action': 'BUY',
                'entry_price': cp,
                'targets': [round(target, 2) for target in targets],
                'stop_loss': round(sl, 2),
                'confidence': 'HIGH',
                'setup': 'VOLUME_BREAKOUT',
                'reason': f"Breakout above ₹{levels['resistance']} with {levels['volume_ratio']:.1f}x volume"
            })

        # STRATEGY 2: SUPPORT REVERSAL (Institutional)
        if (cp <= levels['support'] * 1.005 and 
            levels['volume_ratio'] > 1.5 and
            levels['trend'] == 'BULLISH'):
            
            targets = [cp * (1 + target_pct/100) for target_pct in self.strategies['SWING']['targets']]
            sl = levels['support'] * 0.99
            
            signals.append({
                'strategy': 'SWING',
                'action': 'BUY',
                'entry_price': cp,
                'targets': [round(target, 2) for target in targets],
                'stop_loss': round(sl, 2),
                'confidence': 'HIGH',
                'setup': 'SUPPORT_REVERSAL',
                'reason': f"Strong support bounce at ₹{levels['support']}"
            })

        # STRATEGY 3: MOMENTUM INTRADAY (Professional Day Trading)
        if (levels['volume_ratio'] > 2.0 and
            levels['volatility_pct'] > 1.5 and  # High volatility
            cp > levels['ma_20']):
            
            targets = [cp * (1 + target_pct/100) for target_pct in self.strategies['INTRADAY']['targets']]
            sl = cp * (1 - self.strategies['INTRADAY']['sl']/100)
            
            signals.append({
                'strategy': 'INTRADAY',
                'action': 'BUY',
                'entry_price': cp,
                'targets': [round(target, 2) for target in targets],
                'stop_loss': round(sl, 2),
                'confidence': 'MEDIUM',
                'setup': 'MOMENTUM',
                'reason': f"Momentum play | Volatility: {levels['volatility_pct']:.1f}% | Volume: {levels['volume_ratio']:.1f}x"
            })

        return signals
    
    def calculate_professional_metrics(self, signal):
        """Calculate advanced risk metrics with multiple targets"""
        entry = signal['entry_price']
        stop_loss = signal['stop_loss']
        
        if signal['action'] == 'BUY':
            risk = entry - stop_loss
        else:
            risk = stop_loss - entry
        
        # Calculate profit for each target
        target_profits = []
        for target in signal['targets']:
            if signal['action'] == 'BUY':
                gross_profit = target - entry
            else:
                gross_profit = entry - target
            
            net_profit = gross_profit - self.brokerage
            target_profits.append({
                'target_price': target,
                'gross_profit': round(gross_profit, 2),
                'net_profit': round(net_profit, 2)
            })
        
        # Risk-reward for first target (conservative)
        first_target_reward = target_profits[0]['gross_profit']
        risk_reward = first_target_reward / risk if risk > 0 else 0
        
        # Position sizing based on volatility
        risk_percentage = (risk / entry) * 100
        if risk_percentage < 1:
            position_size = "Aggressive: 3-4% capital"
        elif risk_percentage < 2:
            position_size = "Moderate: 2-3% capital"
        else:
            position_size = "Conservative: 1-2% capital"
        
        return {
            'risk_reward': round(risk_reward, 2),
            'position_size': position_size,
            'target_profits': target_profits,
            'risk_percentage': round(risk_percentage, 2),
            'total_risk': round(risk, 2)
        }
    
    def send_professional_alert(self, message):
        """Send professional Telegram alert"""
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if not token or not chat_id:
            logger.error("❌ Missing Telegram credentials")
            return False
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            response = requests.post(url, data={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Telegram error: {e}")
            return False
    
    def format_professional_signal(self, stock_name, signal, metrics):
        """Create professional alert with multiple profit targets"""
        action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
        
        # Strategy emojis
        strategy_emojis = {
            'BREAKOUT': '🚀',
            'INTRADAY': '⚡', 
            'SWING': '📈',
            'SCALPING': '🎯'
        }
        
        strategy_emoji = strategy_emojis.get(signal['strategy'], '📊')
        
        # Build targets section
        targets_text = ""
        for i, profit_data in enumerate(metrics['target_profits']):
            target_num = i + 1
            targets_text += f"🎯 <b>Target {target_num}:</b> ₹{profit_data['target_price']}\n"
            targets_text += f"   💰 Profit: ₹{profit_data['net_profit']} (after costs)\n"
        
        message = f"""
{action_emoji} <b>ROSHI PROFESSIONAL SIGNAL</b> {strategy_emoji}

<b>Stock:</b> {stock_name}
<b>Strategy:</b> {signal['strategy']}
<b>Action:</b> {signal['action']}
<b>Setup:</b> {signal['setup']}

<b>TRADE EXECUTION:</b>
💰 <b>Entry Price:</b> ₹{signal['entry_price']}
🛑 <b>Stop Loss:</b> ₹{signal['stop_loss']}

<b>PROFIT TARGETS (Multiple Breakouts):</b>
{targets_text}
<b>RISK MANAGEMENT:</b>
📊 <b>Risk-Reward (T1):</b> 1:{metrics['risk_reward']}
💼 <b>Position Size:</b> {metrics['position_size']}
📈 <b>Risk per Trade:</b> {metrics['risk_percentage']}%
✅ <b>Confidence:</b> {signal['confidence']}

<b>STRATEGY INSIGHT:</b>
{signal['reason']}

<b>TRADING PLAN:</b>
• Target 1: Quick profit (conservative)
• Target 2: Medium profit (balanced)  
• Target 3: Maximum profit (aggressive)
• Move SL to cost after Target 1

<b>Strategy by Roshin</b>
⚡ <b>Disclaimer:</b> Trading involves risk

<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
"""
        return message
    
    def is_market_hours(self):
        """Check Indian market hours"""
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()
        
        market_start = dt_time(9, 15)
        market_end = dt_time(15, 30)
        
        return (current_day < 5 and market_start <= current_time <= market_end)
    
    def professional_scan(self):
        """Professional market scanning"""
        if not self.is_market_hours():
            logger.info("⏳ Market closed - Professional scanner active")
            return
            
        logger.info(f"🔍 PROFESSIONAL SCAN - {datetime.now().strftime('%H:%M:%S')}")
        
        signals_found = 0
        for stock_name, stock_code in self.stocks.items():
            try:
                # Get professional data
                data = self.get_professional_data(stock_code)
                if not data:
                    continue
                    
                # Calculate advanced levels
                levels = self.calculate_advanced_levels(data)
                if not levels:
                    continue
                    
                # Generate professional signals
                signals = self.generate_advanced_signals(stock_name, levels)
                
                for signal in signals:
                    # Calculate professional metrics
                    metrics = self.calculate_professional_metrics(signal)
                    
                    # Quality filter - only high probability trades
                    if (metrics['risk_reward'] >= 2.0 and 
                        metrics['target_profits'][0]['net_profit'] >= self.min_profit):
                        
                        alert_key = f"{stock_name}_{signal['strategy']}_{signal['entry_price']}"
                        if alert_key not in self.sent_alerts:
                            message = self.format_professional_signal(stock_name, signal, metrics)
                            if self.send_professional_alert(message):
                                self.sent_alerts[alert_key] = True
                                signals_found += 1
                                logger.info(f"✅ {stock_name} - {signal['strategy']} - RR: 1:{metrics['risk_reward']}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error scanning {stock_name}: {e}")
                continue
        
        if signals_found > 0:
            logger.info(f"🎯 Professional scan complete - {signals_found} high-quality signals")
        else:
            logger.info("✅ Professional scan complete - no quality signals")
    
    def start_professional_scanner(self):
        """Start the professional scanner"""
        logger.info("🚀 ROSHI PROFESSIONAL SCANNER ACTIVATED")
        logger.info("🎯 Multiple Profit Targets | 💰 Higher Profit Margins")
        logger.info("📊 Curated High-Momentum Stocks | ⏰ Professional Strategies")
        
        # Professional startup message
        startup_msg = """
🚀 <b>ROSHI PROFESSIONAL SCANNER - OPTIMIZED</b>

<b>PROFESSIONAL FEATURES:</b>
✅ <b>Multiple Profit Targets</b> (3 breakout points)
✅ <b>Higher Profit Margins</b> (2.0-7.0% targets)
✅ <b>Curated Stock List</b> (15 high-momentum stocks)
✅ <b>Advanced Risk Management</b>
✅ <b>Volume Confirmation</b> required

<b>PROFIT TARGET STRATEGY:</b>
🎯 <b>Target 1:</b> Quick profit (2.0-4.0%)
🎯 <b>Target 2:</b> Medium profit (3.5-6.0%)  
🎯 <b>Target 3:</b> Maximum profit (5.0-7.0%)

<b>TRADING PLAN:</b>
• Take partial profits at each target
• Move stop loss to breakeven after Target 1
• Let winners run to Target 3

<b>Strategy by Roshin</b>
⚡ <b>Disclaimer:</b> Trading involves risk

<i>Professional-grade scanning activated! 🚀</i>
"""
        self.send_professional_alert(startup_msg)
        
        # Schedule professional scans
        schedule.every(2).minutes.do(self.professional_scan)
        
        # Run first scan
        self.professional_scan()
        
        # Keep running
        logger.info("🔄 Professional scanner running...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    scanner = RoshiProfessionalScanner()
    scanner.start_professional_scanner()
