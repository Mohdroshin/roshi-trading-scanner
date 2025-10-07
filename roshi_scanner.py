import pandas as pd
import numpy as np
import yfinance as yf
import requests
import time
import schedule
import os
from datetime import datetime, time as dt_time
from dotenv import load_dotenv
import logging

# Cloud-optimized logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

print("🚀 ROSHI PROFESSIONAL SCANNER - 24/7 Cloud Deployment")
load_dotenv()

class RoshiProfessionalScanner:
    def __init__(self):
        self.brokerage = 40
        self.min_profit = 50
        
        self.strategies = {
            'SCALPING': {'target': 0.8, 'sl': 0.4, 'hold': '5-15min', 'rr': 2.0},
            'INTRADAY': {'target': 1.5, 'sl': 0.7, 'hold': '15min-EOD', 'rr': 2.1},
            'SWING': {'target': 3.5, 'sl': 1.7, 'hold': '1-3 days', 'rr': 2.0},
            'FUTURES': {'target': 2.8, 'sl': 1.3, 'hold': 'Intraday', 'rr': 2.1}
        }
        
        # Optimized stock list for cloud
        self.stocks = {
            'NIFTY50': '^NSEI',
            'BANKNIFTY': '^NSEBANK',
            'RELIANCE': 'RELIANCE.NS', 'TCS': 'TCS.NS', 'HDFCBANK': 'HDFCBANK.NS',
            'ICICIBANK': 'ICICIBANK.NS', 'INFY': 'INFY.NS', 'BHARTIARTL': 'BHARTIARTL.NS',
            'ITC': 'ITC.NS', 'SBIN': 'SBIN.NS', 'KOTAKBANK': 'KOTAKBANK.NS',
            'AXISBANK': 'AXISBANK.NS', 'MARUTI': 'MARUTI.NS', 'TITAN': 'TITAN.NS',
            'SUNPHARMA': 'SUNPHARMA.NS', 'TATAMOTORS': 'TATAMOTORS.NS'
        }
        
        self.sent_alerts = {}

    def get_stock_data(self, symbol):
        """Cloud-optimized data fetching"""
        try:
            data = yf.Ticker(symbol).history(period='2d', interval='15m')
            return data
        except Exception as e:
            logger.error(f"Data error for {symbol}: {e}")
            return pd.DataFrame()

    def calculate_levels(self, data):
        """Calculate technical levels"""
        if data.empty or len(data) < 20:
            return None
            
        cp = data['Close'].iloc[-1]
        support = data['Low'].tail(20).min()
        resistance = data['High'].tail(20).max()
        
        avg_volume = data['Volume'].tail(20).mean()
        current_volume = data['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        ma_20 = data['Close'].tail(20).mean()
        ma_50 = data['Close'].tail(50).mean()
        trend = "BULLISH" if ma_20 > ma_50 else "BEARISH"
        
        return {
            'price': cp, 'support': support, 'resistance': resistance,
            'volume_ratio': volume_ratio, 'trend': trend
        }

    def generate_signals(self, stock_name, levels):
        """Generate trading signals"""
        if not levels: return []
        
        signals = []
        cp = levels['price']
        
        # BREAKOUT STRATEGY
        if (cp >= levels['resistance'] and 
            levels['volume_ratio'] > 1.8 and
            levels['trend'] == 'BULLISH'):
            
            target = cp * (1 + self.strategies['INTRADAY']['target']/100)
            sl = cp * (1 - self.strategies['INTRADAY']['sl']/100)
            
            signals.append({
                'style': 'INTRADAY', 'action': 'BUY', 'entry': cp,
                'target': round(target, 2), 'sl': round(sl, 2),
                'confidence': 'HIGH', 'setup': 'BREAKOUT',
                'reason': f"Breakout ₹{levels['resistance']} | Volume {levels['volume_ratio']:.1f}x"
            })

        # SUPPORT STRATEGY
        if (cp <= levels['support'] * 1.01 and 
            levels['volume_ratio'] > 1.5 and
            levels['trend'] == 'BULLISH'):
            
            target = cp * (1 + self.strategies['SWING']['target']/100)
            sl = levels['support'] * 0.995
            
            signals.append({
                'style': 'SWING', 'action': 'BUY', 'entry': cp,
                'target': round(target, 2), 'sl': round(sl, 2),
                'confidence': 'HIGH', 'setup': 'SUPPORT',
                'reason': f"Support bounce ₹{levels['support']}"
            })

        return signals

    def calculate_risk(self, signal):
        """Risk management"""
        if signal['action'] == 'BUY':
            risk = signal['entry'] - signal['sl']
            reward = signal['target'] - signal['entry']
        else:
            risk = signal['sl'] - signal['entry']
            reward = signal['entry'] - signal['target']
            
        rr_ratio = reward / risk if risk > 0 else 0
        profit = reward - self.brokerage
        
        risk_percent = (risk / signal['entry']) * 100
        position = f"Risk: {risk_percent:.1f}% capital"
        
        return {
            'rr_ratio': round(rr_ratio, 2),
            'net_profit': profit,
            'position': position,
            'profitable': profit > 0
        }

    def send_alert(self, message):
        """Send Telegram alert"""
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not token or not chat_id: 
            logger.error("❌ Missing Telegram credentials")
            return False
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            response = requests.post(url, data={
                'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'
            }, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Telegram error: {e}")
            return False

    def format_alert(self, stock, signal, metrics):
        """Format professional alert"""
        action_emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
        
        message = f"""
{action_emoji} <b>ROSHI CLOUD SIGNAL</b> {action_emoji}

<b>{stock}</b> | {signal['style']} | {signal['setup']}
<b>Entry:</b> ₹{signal['entry']}
<b>Target:</b> ₹{signal['target']} 
<b>Stop Loss:</b> ₹{signal['sl']}

<b>Risk-Reward:</b> 1:{metrics['rr_ratio']}
<b>Position:</b> {metrics['position']}
<b>Confidence:</b> {signal['confidence']}

<b>Strategy:</b> {signal['reason']}

<b>Strategy by Roshin</b>
⚡ <b>Disclaimer:</b> Trading involves risk

<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
"""
        return message

    def is_market_open(self):
        """Check market hours"""
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()
        
        market_start = dt_time(9, 15)
        market_end = dt_time(15, 30)
        
        return (current_day < 5 and market_start <= current_time <= market_end)

    def scan_market(self):
        """Market scanning with cloud optimization"""
        if not self.is_market_open():
            logger.info("⏳ Market closed - Cloud scanner active")
            return
            
        logger.info(f"🔍 ROSHI CLOUD SCAN - {datetime.now().strftime('%H:%M:%S')}")
        
        for stock, code in self.stocks.items():
            try:
                data = self.get_stock_data(code)
                if data.empty: continue
                    
                levels = self.calculate_levels(data)
                if not levels: continue
                    
                signals = self.generate_signals(stock, levels)
                
                for signal in signals:
                    metrics = self.calculate_risk(signal)
                    
                    if metrics['rr_ratio'] >= 1.8 and metrics['profitable']:
                        alert_key = f"{stock}_{signal['style']}"
                        if alert_key in self.sent_alerts:
                            if (datetime.now() - self.sent_alerts[alert_key]).seconds < 1800:
                                continue
                                
                        message = self.format_alert(stock, signal, metrics)
                        if self.send_alert(message):
                            self.sent_alerts[alert_key] = datetime.now()
                            logger.info(f"✅ {stock} - {signal['style']}")
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ {stock}: {e}")
                continue

    def start_cloud_scanner(self):
        """Start 24/7 cloud scanner"""
        logger.info("🚀 ROSHI 24/7 CLOUD SCANNER ACTIVATED")
        logger.info("☁️  Running on Render Cloud")
        logger.info("⏰ Market hours scanning | 🔄 2-minute intervals")
        logger.info("📊 15+ Stocks & Indices")
        
        # Cloud startup message
        startup_msg = """
🚀 <b>ROSHI 24/7 CLOUD SCANNER ACTIVATED</b>

✅ <b>Now running 24/7 on Render Cloud</b>
✅ <b>Automatic market hours detection</b>
✅ <b>15+ Stocks & Indices</b>
✅ <b>Professional strategies</b>
⏰ <b>Scan interval:</b> Every 2 minutes during market hours

<b>Strategy by Roshin</b>
⚡ <b>Disclaimer:</b> Trading involves risk

<i>Your scanner is now running 24/7 in the cloud! 🚀</i>
"""
        self.send_alert(startup_msg)
        
        # Schedule scans
        schedule.every(2).minutes.do(self.scan_market)
        
        # Run first scan
        self.scan_market()
        
        # Cloud-optimized continuous operation
        logger.info("🔄 ROSHI Cloud Scanner running 24/7...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(60)  # Wait 1 minute and restart

if __name__ == "__main__":
    scanner = RoshiProfessionalScanner()
    scanner.start_cloud_scanner()
