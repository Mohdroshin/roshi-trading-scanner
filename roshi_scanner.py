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

print("🚀 ROSHI SCANNER - Replit Cloud")
print("✅ Free 24/7 Hosting | ⏰ Market Hours | 🔄 2-min Scans")

class RoshiScanner:
    def __init__(self):
        self.brokerage = 40
        self.min_profit = 50
        
        self.strategies = {
            'SCALPING': {'target': 0.8, 'sl': 0.4, 'hold': '5-15min'},
            'INTRADAY': {'target': 1.5, 'sl': 0.7, 'hold': '15min-EOD'},
            'SWING': {'target': 3.5, 'sl': 1.7, 'hold': '1-3 days'}
        }
        
        # 15 key stocks for free tier
        self.stocks = {
            'NIFTY50': '^NSEI',
            'BANKNIFTY': '^NSEBANK',
            'RELIANCE': 'RELIANCE.NS', 'TCS': 'TCS.NS', 'HDFCBANK': 'HDFCBANK.NS',
            'ICICIBANK': 'ICICIBANK.NS', 'INFY': 'INFY.NS', 'BHARTIARTL': 'BHARTIARTL.NS',
            'SBIN': 'SBIN.NS', 'KOTAKBANK': 'KOTAKBANK.NS', 'AXISBANK': 'AXISBANK.NS',
            'MARUTI': 'MARUTI.NS', 'TITAN': 'TITAN.NS', 'ITC': 'ITC.NS'
        }
        
        self.sent_alerts = {}
    
    def get_price(self, symbol):
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period='1d', interval='1m')
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            logger.error(f"Price error for {symbol}: {e}")
            return None
    
    def send_alert(self, message):
        # Works on Replit (secrets) and local (.env)
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
                'parse_mode': 'HTML'
            }, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Alert sent to Telegram")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Telegram error: {e}")
            return False
    
    def scan_single_stock(self, stock_name, stock_code):
        price = self.get_price(stock_code)
        if not price:
            return None
        
        # Simple breakout strategy
        try:
            stock = yf.Ticker(stock_code)
            hist = stock.history(period='2d')
            if len(hist) < 2:
                return None
            
            prev_close = hist['Close'].iloc[0]
            current_price = hist['Close'].iloc[-1]
            
            # Buy if price increased 0.3% from previous close
            if current_price >= prev_close * 1.003:
                target = current_price * 1.015  # 1.5% target
                sl = current_price * 0.99       # 1% stop loss
                profit = (target - current_price) - self.brokerage
                
                if profit > self.min_profit:
                    return {
                        'action': 'BUY',
                        'entry': round(current_price, 2),
                        'target': round(target, 2),
                        'sl': round(sl, 2),
                        'profit': round(profit, 2),
                        'reason': 'Breakout momentum'
                    }
        except Exception as e:
            logger.error(f"Strategy error for {stock_name}: {e}")
        
        return None
    
    def format_alert(self, stock, signal):
        return f"""
🟢 <b>ROSHI SIGNAL - REPLIT CLOUD</b> 🟢

<b>{stock}</b> | INTRADAY | BREAKOUT
<b>Entry:</b> ₹{signal['entry']}
<b>Target:</b> ₹{signal['target']}
<b>Stop Loss:</b> ₹{signal['sl']}

<b>Expected Profit:</b> ₹{signal['profit']} (after brokerage)
<b>Strategy:</b> {signal['reason']}

<b>Strategy by Roshin</b>
⚡ <b>Disclaimer:</b> Trading involves risk

<b>Time:</b> {datetime.now().strftime('%H:%M:%S')}
"""
    
    def is_market_open(self):
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()
        
        market_start = dt_time(9, 15)
        market_end = dt_time(15, 30)
        
        return (current_day < 5 and market_start <= current_time <= market_end)
    
    def scan_market(self):
        if not self.is_market_open():
            logger.info("⏳ Market closed - Scanner active")
            return
            
        logger.info(f"🔍 ROSHI SCAN - {datetime.now().strftime('%H:%M:%S')}")
        
        signals_found = 0
        for stock, code in self.stocks.items():
            try:
                signal = self.scan_single_stock(stock, code)
                if signal:
                    alert_key = f"{stock}_{signal['entry']}"
                    if alert_key not in self.sent_alerts:
                        message = self.format_alert(stock, signal)
                        if self.send_alert(message):
                            self.sent_alerts[alert_key] = True
                            signals_found += 1
                            logger.info(f"✅ Signal for {stock} at ₹{signal['entry']}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Scan error for {stock}: {e}")
                continue
        
        if signals_found > 0:
            logger.info(f"🎯 Found {signals_found} signals")
        else:
            logger.info("✅ Scan complete - no signals")
    
    def start_replit(self):
        logger.info("🚀 ROSHI Scanner Started on Replit Cloud")
        logger.info("📊 15 Stocks & Indices")
        logger.info("⏰ Market Hours | 🔄 2-min Scans")
        
        # Startup message
        startup_msg = """
🚀 <b>ROSHI SCANNER - REPLIT CLOUD</b>

✅ <b>Now running 24/7 on Replit Cloud</b>
✅ <b>Free hosting - No costs</b>
✅ <b>15 Stocks & Indices</b>
✅ <b>Automatic market hours detection</b>
⏰ <b>Scan interval:</b> Every 2 minutes

<b>Strategy by Roshin</b>
⚡ <b>Disclaimer:</b> Trading involves risk

<i>Your professional scanner is now live! 🚀</i>
"""
        self.send_alert(startup_msg)
        
        # Schedule scans every 2 minutes
        schedule.every(2).minutes.do(self.scan_market)
        
        # Run first scan
        self.scan_market()
        
        # Keep alive forever
        logger.info("🔄 ROSHI running 24/7 on Replit...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    scanner = RoshiScanner()
    scanner.start_replit()
