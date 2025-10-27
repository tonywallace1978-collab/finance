"""
Batch Price Fetcher for Financial Tracker

Efficiently fetches prices for 77+ assets using batch API calls:
- CoinGecko: Fetch ALL cryptos in 1-2 requests (supports 250 coins per call)
- yfinance: Fetch stocks/ETFs with rate limiting
- Location-aware BTC handling (ETF vs actual Bitcoin)
"""

import yfinance as yf
import requests
from datetime import datetime
from app_complete import db, Asset, AssetPrice
import time

# CoinGecko crypto mappings
CRYPTO_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'COMP': 'compound-coin',  # NOT compound-governance-token
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

class BatchPriceFetcher:
    """Efficient batch price fetching for multiple assets"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_all_crypto_prices_batch(self, crypto_tickers):
        """
        Fetch ALL crypto prices in a single CoinGecko API call
        CoinGecko supports up to 250 coin IDs per request
        """
        if not crypto_tickers:
            return {}

        # Map tickers to CoinGecko IDs
        coin_ids = []
        ticker_to_id = {}

        for ticker in crypto_tickers:
            coin_id = CRYPTO_MAP.get(ticker)
            if coin_id:
                coin_ids.append(coin_id)
                ticker_to_id[coin_id] = ticker

        if not coin_ids:
            return {}

        try:
            # Fetch ALL coins in one request
            ids_param = ','.join(coin_ids)
            url = f'https://api.coingecko.com/api/v3/simple/price'
            params = {
                'ids': ids_param,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Convert back to ticker format
            prices = {}
            for coin_id, coin_data in data.items():
                ticker = ticker_to_id.get(coin_id)
                if ticker and 'usd' in coin_data:
                    prices[ticker] = {
                        'price': coin_data['usd'],
                        'change_percent': coin_data.get('usd_24h_change', 0),
                        'change_dollar': 0  # Calculate from percent
                    }
                    # Calculate dollar change from percent
                    if prices[ticker]['change_percent']:
                        prev_price = prices[ticker]['price'] / (1 + prices[ticker]['change_percent'] / 100)
                        prices[ticker]['change_dollar'] = prices[ticker]['price'] - prev_price

            print(f"✓ Fetched {len(prices)} crypto prices in single batch call")
            return prices

        except Exception as e:
            print(f"✗ Batch crypto fetch failed: {e}")
            return {}

    def fetch_stock_price(self, ticker):
        """Fetch single stock/ETF price using yfinance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if not current_price:
                # Try getting from history
                hist = stock.history(period='1d')
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]

            if not current_price:
                return None

            # Get previous close for change calculation
            prev_close = info.get('previousClose', current_price)
            change_dollar = current_price - prev_close
            change_percent = (change_dollar / prev_close * 100) if prev_close else 0

            return {
                'price': float(current_price),
                'change_dollar': float(change_dollar),
                'change_percent': float(change_percent)
            }

        except Exception as e:
            print(f"✗ Failed to fetch {ticker}: {e}")
            return None

    def fetch_stocks_batch(self, tickers):
        """Fetch multiple stocks with rate limiting"""
        prices = {}

        for ticker in tickers:
            price_data = self.fetch_stock_price(ticker)
            if price_data:
                prices[ticker] = price_data
                print(f"✓ {ticker}: ${price_data['price']:.2f}")
            else:
                print(f"✗ {ticker}: Failed")

            # Rate limiting - be respectful
            time.sleep(0.2)

        return prices

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
            return True
        except Exception as e:
            print(f"✗ Failed to save {ticker} price to DB: {e}")
            return False

    def update_all_prices(self):
        """Update prices for all assets in database"""
        assets = Asset.query.all()

        # Group assets by type and location
        crypto_tickers = set()
        stock_tickers = set()
        btc_locations = {}  # Track BTC by location

        for asset in assets:
            if asset.ticker == 'BTC':
                btc_locations[asset.location] = asset.ticker
            elif asset.classification == 'Crypto':
                crypto_tickers.add(asset.ticker)
            else:  # Stock or ETF
                stock_tickers.add(asset.ticker)

        print(f"\n=== Batch Price Update ===")
        print(f"Crypto assets: {len(crypto_tickers)}")
        print(f"Stock/ETF assets: {len(stock_tickers)}")
        print(f"BTC locations: {list(btc_locations.keys())}")

        updated = 0
        failed = 0

        # 1. Fetch ALL crypto prices in single batch call
        print("\n[1/3] Fetching crypto prices (batch)...")
        crypto_prices = self.fetch_all_crypto_prices_batch(list(crypto_tickers))

        # Save crypto prices
        for asset in assets:
            if asset.classification == 'Crypto' and asset.ticker != 'BTC':
                if asset.ticker in crypto_prices:
                    if self.save_price_to_db(asset.ticker, asset.location, crypto_prices[asset.ticker]):
                        updated += 1
                    else:
                        failed += 1
                else:
                    failed += 1

        db.session.commit()

        # 2. Handle BTC separately (location-aware)
        print("\n[2/3] Fetching BTC prices (location-aware)...")
        for location, ticker in btc_locations.items():
            if location == 'Etrade':
                # BTC ETF - use stock API
                price_data = self.fetch_stock_price('BTC')
                if price_data:
                    if self.save_price_to_db('BTC', location, price_data):
                        print(f"✓ BTC (Etrade ETF): ${price_data['price']:.2f}")
                        updated += 1
                    else:
                        failed += 1
                else:
                    failed += 1
            else:
                # Actual Bitcoin - use crypto API
                btc_crypto = self.fetch_all_crypto_prices_batch(['BTC'])
                if 'BTC' in btc_crypto:
                    if self.save_price_to_db('BTC', location, btc_crypto['BTC']):
                        print(f"✓ BTC ({location}): ${btc_crypto['BTC']['price']:,.2f}")
                        updated += 1
                    else:
                        failed += 1
                else:
                    failed += 1

        db.session.commit()

        # 3. Fetch stock/ETF prices
        print(f"\n[3/3] Fetching {len(stock_tickers)} stock/ETF prices...")
        stock_prices = self.fetch_stocks_batch(list(stock_tickers))

        # Save stock prices
        for asset in assets:
            if asset.classification in ['Stock', 'ETF'] and asset.ticker != 'BTC':
                if asset.ticker in stock_prices:
                    if self.save_price_to_db(asset.ticker, asset.location, stock_prices[asset.ticker]):
                        updated += 1
                    else:
                        failed += 1
                else:
                    failed += 1

        db.session.commit()

        print(f"\n=== Update Complete ===")
        print(f"✓ Updated: {updated}")
        print(f"✗ Failed: {failed}")
        print(f"Total: {updated + failed}\n")

        return updated, failed


def update_all_prices_batch():
    """Standalone function for API endpoint"""
    fetcher = BatchPriceFetcher()
    return fetcher.update_all_prices()


if __name__ == '__main__':
    # Test the batch fetcher
    from app_complete import app

    with app.app_context():
        print("Testing Batch Price Fetcher...")
        update_all_prices_batch()
