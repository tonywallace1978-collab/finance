import yfinance as yf
import requests
from datetime import datetime, timedelta
from models import db, AssetPrice
import time

# CoinGecko mappings for crypto tickers
CRYPTO_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'COMP': 'compound-coin',  # NOT compound-governance-token
    'HBAR': 'hedera',
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
    'MATIC': 'polygon',
    'UNI': 'uniswap',
    'AVAX': 'avalanche-2',
}

class PriceFetcher:
    """Service to fetch prices from yfinance and CoinGecko"""

    def __init__(self):
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.price_cache = {}  # In-memory cache for prices

    def fetch_stock_price(self, ticker):
        """Fetch stock/ETF price using yfinance"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")

            if len(hist) < 1:
                print(f"No data for {ticker}")
                return None

            current_price = hist['Close'].iloc[-1]

            # Calculate change
            change_dollar = 0
            change_percent = 0
            if len(hist) >= 2:
                prev_price = hist['Close'].iloc[-2]
                change_dollar = current_price - prev_price
                change_percent = (change_dollar / prev_price) * 100

            return {
                'price': round(current_price, 2),
                'change_dollar': round(change_dollar, 2),
                'change_percent': round(change_percent, 2)
            }
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
            return None

    def fetch_crypto_price(self, ticker):
        """Fetch cryptocurrency price using CoinGecko API"""
        try:
            if ticker not in CRYPTO_MAP:
                print(f"No CoinGecko mapping for {ticker}")
                return None

            coin_id = CRYPTO_MAP[ticker]

            # Fetch current price and 24h change
            url = f"{self.coingecko_base_url}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if coin_id not in data:
                print(f"No data for {coin_id}")
                return None

            price = data[coin_id]['usd']
            change_percent = data[coin_id].get('usd_24h_change', 0)
            change_dollar = (price * change_percent) / 100

            return {
                'price': round(price, 2),
                'change_dollar': round(change_dollar, 2),
                'change_percent': round(change_percent, 2)
            }
        except Exception as e:
            print(f"Error fetching crypto price for {ticker}: {e}")
            return None

    def fetch_price(self, asset):
        """
        Fetch price for an asset based on its classification and location.
        Special handling for BTC:
        - If location is 'Etrade', fetch as stock (BTC ETF)
        - If location is 'Hard Wallet', fetch as crypto (actual Bitcoin)
        """
        ticker = asset.ticker
        classification = asset.classification
        location = asset.location

        # Special BTC handling
        if ticker == 'BTC':
            if location == 'Etrade':
                # This is the Grayscale Bitcoin Mini Trust ETF
                price_data = self.fetch_stock_price(ticker)
            elif location in ['Hard Wallet', 'Coinbase']:
                # This is actual Bitcoin cryptocurrency
                price_data = self.fetch_crypto_price(ticker)
            else:
                print(f"Unknown location for BTC: {location}")
                return None
        elif classification in ['Stock', 'ETF']:
            price_data = self.fetch_stock_price(ticker)
        elif classification == 'Crypto':
            price_data = self.fetch_crypto_price(ticker)
        else:
            print(f"Unknown classification: {classification}")
            return None

        if price_data:
            # Cache the price with location context
            cache_key = f"{ticker}_{location}"
            self.price_cache[cache_key] = price_data

        return price_data

    def get_cached_price(self, ticker, location):
        """Get cached price for a specific ticker and location"""
        cache_key = f"{ticker}_{location}"
        return self.price_cache.get(cache_key)

    def update_all_prices(self, assets):
        """Update prices for all assets and save to database"""
        updated_count = 0
        failed_count = 0

        print(f"\nUpdating prices for {len(assets)} assets...")

        for asset in assets:
            price_data = self.fetch_price(asset)

            if price_data:
                # Save to database
                asset_price = AssetPrice(
                    ticker=asset.ticker,
                    price=price_data['price'],
                    change_dollar=price_data['change_dollar'],
                    change_percent=price_data['change_percent'],
                    location=asset.location,  # Store location for BTC differentiation
                    timestamp=datetime.utcnow()
                )
                db.session.add(asset_price)
                updated_count += 1
                print(f"✓ {asset.ticker} ({asset.location}): ${price_data['price']}")
            else:
                failed_count += 1
                print(f"✗ {asset.ticker} ({asset.location}): Failed to fetch price")

            # Be nice to APIs - add small delay
            time.sleep(0.2)

        db.session.commit()
        print(f"\nPrice update complete: {updated_count} updated, {failed_count} failed")
        return updated_count, failed_count

    def get_latest_price(self, ticker, location):
        """Get the latest price from database for a specific ticker and location"""
        price_record = AssetPrice.query.filter_by(
            ticker=ticker,
            location=location
        ).order_by(AssetPrice.timestamp.desc()).first()

        return price_record
