"""
Robust Price Fetcher with Multiple Fallback Mechanisms

This fetcher NEVER fails. It tries multiple data sources:
1. Primary APIs (yfinance, CoinGecko)
2. Alternative APIs (direct Yahoo Finance, CoinMarketCap)
3. Web search as last resort

CRITICAL: Every asset MUST get a price when requested.
"""

import yfinance as yf
import requests
from datetime import datetime
from models import db, Asset, AssetPrice
import time
import re

# CoinGecko crypto mappings
CRYPTO_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'COMP': 'compound-coin',
    'HBAR': 'hedera-hashgraph',
    'WLFI': 'world-liberty-financial-wlfi',
    'WLD': 'worldcoin-wld',
    'PAXG': 'pax-gold',
    'DOT': 'polkadot',
    'FLR': 'flare-networks',
    'CGLD': 'celo',
    'NU': 'nucypher',
    'SOL': 'solana',
    'ADA': 'cardano',
    'LINK': 'chainlink',
    'XRP': 'ripple',
    'DOGE': 'dogecoin',
    'MATIC': 'polygon-ecosystem-token',
    'UNI': 'uniswap',
    'AVAX': 'avalanche-2',
    'LTC': 'litecoin',
    'BCH': 'bitcoin-cash',
    'XLM': 'stellar',
    'ALGO': 'algorand',
    'ATOM': 'cosmos',
    'FET': 'fetch-ai',
    'GRT': 'the-graph',
    'SAND': 'the-sandbox',
    'MANA': 'decentraland',
    'AAVE': 'aave',
    'MKR': 'maker',
    'SNX': 'synthetix-network-token',
    'SUSHI': 'sushi',
    'CRV': 'curve-dao-token',
    '1INCH': '1inch',
    'YFI': 'yearn-finance',
    'BAT': 'basic-attention-token',
    'ENJ': 'enjincoin',
    'ZRX': '0x',
    'SHIB': 'shiba-inu',
}


class RobustPriceFetcher:
    """Price fetcher that NEVER fails - uses multiple fallback mechanisms"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.failed_tickers = []

    def fetch_stock_yfinance(self, ticker):
        """Try fetching stock price using yfinance"""
        try:
            stock = yf.Ticker(ticker)

            # Try multiple methods
            try:
                data = stock.history(period='5d', interval='1d')
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    if len(data) > 1:
                        prev_close = data['Close'].iloc[-2]
                    else:
                        prev_close = current_price

                    change_dollar = current_price - prev_close
                    change_percent = (change_dollar / prev_close * 100) if prev_close else 0

                    return {
                        'price': float(current_price),
                        'change_dollar': float(change_dollar),
                        'change_percent': float(change_percent)
                    }
            except:
                pass

            # Try fast_info
            try:
                info = stock.fast_info
                current_price = info.last_price
                prev_close = info.previous_close

                if current_price and current_price > 0:
                    change_dollar = current_price - prev_close if prev_close else 0
                    change_percent = (change_dollar / prev_close * 100) if prev_close else 0

                    return {
                        'price': float(current_price),
                        'change_dollar': float(change_dollar),
                        'change_percent': float(change_percent)
                    }
            except:
                pass

        except Exception as e:
            print(f"  yfinance failed for {ticker}: {e}")

        return None

    def fetch_stock_yahoo_direct(self, ticker):
        """Fetch directly from Yahoo Finance API"""
        try:
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
            params = {
                'interval': '1d',
                'range': '5d'
            }

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()

                if 'chart' in data and 'result' in data['chart']:
                    result = data['chart']['result'][0]

                    # Get current price
                    meta = result.get('meta', {})
                    current_price = meta.get('regularMarketPrice')
                    prev_close = meta.get('chartPreviousClose')

                    if current_price:
                        change_dollar = current_price - prev_close if prev_close else 0
                        change_percent = (change_dollar / prev_close * 100) if prev_close else 0

                        return {
                            'price': float(current_price),
                            'change_dollar': float(change_dollar),
                            'change_percent': float(change_percent)
                        }
        except Exception as e:
            print(f"  Yahoo direct API failed for {ticker}: {e}")

        return None

    def fetch_crypto_coingecko(self, ticker):
        """Fetch crypto price from CoinGecko"""
        coin_id = CRYPTO_MAP.get(ticker)
        if not coin_id:
            return None

        try:
            url = f'https://api.coingecko.com/api/v3/simple/price'
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }

            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()

                if coin_id in data and 'usd' in data[coin_id]:
                    price = data[coin_id]['usd']
                    change_percent = data[coin_id].get('usd_24h_change', 0)

                    # Calculate dollar change from percent
                    prev_price = price / (1 + change_percent / 100) if change_percent else price
                    change_dollar = price - prev_price

                    return {
                        'price': float(price),
                        'change_dollar': float(change_dollar),
                        'change_percent': float(change_percent)
                    }
            elif response.status_code == 429:
                print(f"  CoinGecko rate limit hit for {ticker}, will retry...")
                time.sleep(2)  # Wait before retry
                return None
        except Exception as e:
            print(f"  CoinGecko failed for {ticker}: {e}")

        return None

    def fetch_crypto_coinmarketcap_free(self, ticker):
        """Try CoinMarketCap free API (no key required for basic quotes)"""
        try:
            # CoinMarketCap web scraping approach
            search_url = f'https://coinmarketcap.com/currencies/{CRYPTO_MAP.get(ticker, ticker.lower())}/'

            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                # Extract price from HTML
                text = response.text

                # Look for price in meta tags or JSON-LD
                price_match = re.search(r'"price":\s*"?\$?([\d,]+\.?\d*)"?', text)
                if price_match:
                    price_str = price_match.group(1).replace(',', '')
                    price = float(price_str)

                    # Look for 24h change
                    change_match = re.search(r'<span[^>]*>([+-]?\d+\.?\d*)%</span>', text)
                    change_percent = float(change_match.group(1)) if change_match else 0

                    prev_price = price / (1 + change_percent / 100) if change_percent else price
                    change_dollar = price - prev_price

                    return {
                        'price': float(price),
                        'change_dollar': float(change_dollar),
                        'change_percent': float(change_percent)
                    }
        except Exception as e:
            print(f"  CoinMarketCap scraping failed for {ticker}: {e}")

        return None

    def fetch_with_web_scrape(self, ticker, classification):
        """Web scrape from Yahoo Finance or Google Finance as last resort"""
        try:
            # Try Yahoo Finance quote page
            url = f'https://finance.yahoo.com/quote/{ticker}'
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                text = response.text

                # Look for price in various formats
                patterns = [
                    r'data-symbol="{}"[^>]*data-field="regularMarketPrice"[^>]*data-value="([\d.]+)"'.format(ticker),
                    r'"regularMarketPrice":\{"raw":([\d.]+)',
                    r'data-reactid="\d+">([0-9,]+\.\d+)</span>',
                    r'<fin-streamer[^>]*data-symbol="{}"[^>]*data-field="regularMarketPrice"[^>]*>([0-9,]+\.\d+)</fin-streamer>'.format(ticker)
                ]

                for pattern in patterns:
                    match = re.search(pattern, text)
                    if match:
                        price_str = match.group(1).replace(',', '')
                        price = float(price_str)

                        if price > 0:
                            print(f"  Found price via web scraping")
                            return {
                                'price': price,
                                'change_dollar': 0,
                                'change_percent': 0
                            }

        except Exception as e:
            print(f"  Web scraping failed for {ticker}: {e}")

        # Try Google search as absolute last resort
        try:
            url = f'https://www.google.com/search?q={ticker}+stock+price'
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                text = response.text

                # Look for price patterns
                patterns = [
                    r'data-value="([\d.]+)"',
                    r'>\$?([\d,]+\.\d{2})<',
                ]

                for pattern in patterns:
                    match = re.search(pattern, text)
                    if match:
                        price_str = match.group(1).replace(',', '')
                        try:
                            price = float(price_str)
                            if 0.01 < price < 1000000:  # Sanity check
                                print(f"  Found price via Google search")
                                return {
                                    'price': price,
                                    'change_dollar': 0,
                                    'change_percent': 0
                                }
                        except:
                            continue

        except Exception as e:
            print(f"  Google search scraping failed for {ticker}: {e}")

        return None

    def fetch_price_with_fallbacks(self, ticker, classification, location=None):
        """
        Fetch price with multiple fallback mechanisms
        CRITICAL: This function MUST return a price, never None
        """
        print(f"  Fetching {ticker} ({classification} at {location})...")

        # For stocks and ETFs
        if classification in ['Stock', 'ETF']:
            # Try 1: yfinance
            result = self.fetch_stock_yfinance(ticker)
            if result:
                print(f"  ✓ {ticker}: ${result['price']:.2f} (yfinance)")
                return result

            time.sleep(0.5)  # Rate limiting

            # Try 2: Yahoo Finance direct API
            result = self.fetch_stock_yahoo_direct(ticker)
            if result:
                print(f"  ✓ {ticker}: ${result['price']:.2f} (Yahoo direct)")
                return result

            time.sleep(1)  # More aggressive wait

            # Try 3: Web scraping (last resort)
            print(f"  API methods failed for {ticker}, trying web scraping...")
            result = self.fetch_with_web_scrape(ticker, classification)
            if result:
                print(f"  ✓ {ticker}: ${result['price']:.2f} (web scraping)")
                return result

        # For crypto
        elif classification == 'Crypto':
            # Special handling for BTC at E*Trade (it's the ETF)
            if ticker == 'BTC' and location == 'Etrade':
                return self.fetch_price_with_fallbacks('BTC', 'ETF', location)

            # Try 1: CoinGecko
            result = self.fetch_crypto_coingecko(ticker)
            if result:
                print(f"  ✓ {ticker}: ${result['price']:,.2f} (CoinGecko)")
                return result

            time.sleep(1)  # Rate limiting between attempts

            # Try 2: CoinMarketCap scraping
            result = self.fetch_crypto_coinmarketcap_free(ticker)
            if result:
                print(f"  ✓ {ticker}: ${result['price']:,.2f} (CoinMarketCap)")
                return result

            time.sleep(1)

            # Try 3: Web scraping (last resort)
            print(f"  API methods failed for {ticker}, trying web scraping...")
            result = self.fetch_with_web_scrape(ticker, classification)
            if result:
                print(f"  ✓ {ticker}: ${result['price']:,.2f} (web scraping)")
                return result

        # If ALL methods failed, record it but return a placeholder
        print(f"  ✗ {ticker}: ALL METHODS FAILED - using last known price or 0")
        self.failed_tickers.append(ticker)

        # Try to get last known price from database
        try:
            last_price = AssetPrice.query.filter_by(
                ticker=ticker,
                location=location
            ).order_by(AssetPrice.timestamp.desc()).first()

            if last_price:
                print(f"  → Using last known price: ${last_price.price:.2f}")
                return {
                    'price': last_price.price,
                    'change_dollar': 0,
                    'change_percent': 0
                }
        except:
            pass

        # Absolute last resort: return 0
        return {
            'price': 0.0,
            'change_dollar': 0.0,
            'change_percent': 0.0
        }

    def save_price_to_db(self, ticker, location, price_data):
        """Save price to database"""
        try:
            price_record = AssetPrice(
                ticker=ticker,
                location=location,
                price=price_data['price'],
                change_dollar=price_data.get('change_dollar', 0),
                change_percent=price_data.get('change_percent', 0),
                timestamp=datetime.utcnow()
            )
            db.session.add(price_record)
            db.session.commit()
            return True
        except Exception as e:
            print(f"  ✗ Failed to save {ticker} price to DB: {e}")
            db.session.rollback()
            return False

    def update_all_prices(self):
        """Update prices for all assets - NEVER FAILS"""
        assets = Asset.query.all()

        print(f"\n=== Robust Price Update ({len(assets)} assets) ===")
        print("Using multiple data sources with fallbacks\n")

        updated = 0
        self.failed_tickers = []

        for i, asset in enumerate(assets, 1):
            print(f"[{i}/{len(assets)}] {asset.ticker} at {asset.location}")

            # Fetch price with all fallback mechanisms
            price_data = self.fetch_price_with_fallbacks(
                asset.ticker,
                asset.classification,
                asset.location
            )

            # Save to database
            if self.save_price_to_db(asset.ticker, asset.location, price_data):
                updated += 1

            # Rate limiting between assets
            time.sleep(0.3)

        failed = len(self.failed_tickers)

        print(f"\n=== Update Complete ===")
        print(f"✓ Updated: {updated}/{len(assets)}")
        if failed > 0:
            print(f"⚠ Failed (using fallback): {failed}")
            print(f"  Tickers: {', '.join(self.failed_tickers)}")
        print()

        return updated, failed


def update_all_prices_batch():
    """Entry point for batch price updates"""
    fetcher = RobustPriceFetcher()
    return fetcher.update_all_prices()


if __name__ == '__main__':
    from app import app

    with app.app_context():
        print("Testing Robust Price Fetcher...")
        update_all_prices_batch()
