# Financial Tracker

A Flask-based financial portfolio tracking application that handles stocks, ETFs, and cryptocurrencies across multiple accounts (E*Trade, Coinbase, Hard Wallet).

## Key Features

- **Multi-location portfolio tracking** across E*Trade, Coinbase, and Hard Wallet
- **Automatic price fetching** from yfinance (stocks/ETFs) and CoinGecko (crypto)
- **Special BTC handling** - correctly differentiates between BTC ETF and actual Bitcoin
- **Real-time portfolio valuations** with gain/loss calculations
- **Responsive dashboard** with Bootstrap styling
- **Separate views** for each location and a consolidated portfolio view

## The BTC Dual-Ticker Problem (SOLVED)

### The Problem
The ticker "BTC" is used for TWO different assets:
1. **BTC in E*Trade** = Grayscale Bitcoin Mini Trust ETF (~$51 price)
2. **BTC in Hard Wallet** = Actual Bitcoin cryptocurrency (~$115,000 price)

Using the same price for both would be catastrophically wrong.

### The Solution
The application uses **location-aware price fetching**:

```python
# In price_fetcher.py
if ticker == 'BTC':
    if location == 'Etrade':
        # Fetch as stock/ETF using yfinance
        price_data = self.fetch_stock_price(ticker)
    elif location in ['Hard Wallet', 'Coinbase']:
        # Fetch as crypto using CoinGecko
        price_data = self.fetch_crypto_price(ticker)
```

The `AssetPrice` table includes a `location` field to maintain separate price records:
- `BTC` at `Etrade` = $51.xx (ETF price)
- `BTC` at `Hard Wallet` = $115,000.xx (actual Bitcoin price)

## Project Structure

```
finance/
├── app.py                 # Main Flask application with routes
├── models.py              # Database models (Asset, AssetPrice)
├── price_fetcher.py       # Price fetching service (yfinance + CoinGecko)
├── init_db.py             # Database initialization script
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── stocks.html
│   ├── crypto_coinbase.html
│   ├── crypto_l.html
│   └── portfolio.html
└── instance/              # Database location
    └── finance.db
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

**Option A: Use sample data to test**
```bash
python init_db.py sample
```

**Option B: Import your existing database**
```bash
# Copy your database file
cp /path/to/your/finance.db instance/finance.db

# Update prices
python init_db.py update-prices
```

**Option C: Start fresh**
```bash
python init_db.py init
# Then manually add your assets or import from Excel
```

### 3. Run the Application

```bash
python app.py
```

Visit: http://localhost:5000

## Application Routes

- `/` - Dashboard with overview of all locations
- `/stocks` - E*Trade portfolio (stocks and ETFs)
- `/crypto-coinbase` - Coinbase crypto holdings
- `/crypto-l` - Hard Wallet (L Wallet) crypto holdings
- `/portfolio` - Complete portfolio across all locations
- `/update-prices` - Manually trigger price updates

## Database Schema

### Asset Table
```sql
- id (Primary Key)
- ticker (e.g., 'BTC', 'AAPL')
- classification (Stock, ETF, Crypto)
- quantity (shares/coins)
- price_paid (average cost basis)
- location (Etrade, Coinbase, Hard Wallet)
- company_name (optional)
```

### AssetPrice Table
```sql
- id (Primary Key)
- ticker
- price
- change_dollar (daily change)
- change_percent (daily change %)
- timestamp
- location (crucial for BTC differentiation)
```

## CoinGecko Crypto Mappings

The application includes correct CoinGecko mappings for all major cryptocurrencies:

```python
CRYPTO_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'COMP': 'compound-coin',      # NOT compound-governance-token
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
```

## Expected Portfolio Values

Based on your data, the application should show approximately:
- **E*Trade**: $590,301
- **Coinbase**: $91,516
- **Hard Wallet**: $479,295
- **Total Net Worth**: ~$1,161,112

## API Endpoints

- `GET /api/assets` - Returns all assets as JSON
- `GET /api/prices/<ticker>/<location>` - Returns latest price for specific asset

## Updating Prices

Prices can be updated in three ways:

1. **Manual update** - Click "Update Prices" in the navigation
2. **Python script** - Run `python init_db.py update-prices`
3. **API call** - GET request to `/update-prices`

The price fetcher includes rate limiting (0.2s delay between requests) to be respectful to APIs.

## Important Notes

### API Rate Limits
- yfinance: Generally no strict limits for basic usage
- CoinGecko (free tier): 10-30 calls/minute

### Price Data
- Stock/ETF prices: From yfinance (previous close + today's change)
- Crypto prices: From CoinGecko (current price + 24h change)

### BTC Handling
The app automatically detects BTC ticker and routes to the correct price source based on location. No manual intervention needed!

## Troubleshooting

### Prices not updating?
```bash
python init_db.py update-prices
```

### Database errors?
```bash
# Backup your data first!
python init_db.py init
# Then re-import your data
```

### Wrong BTC price?
Check that:
1. BTC in E*Trade has location = 'Etrade' and classification = 'ETF'
2. BTC in Hard Wallet has location = 'Hard Wallet' and classification = 'Crypto'

## Adding New Assets

You can add assets directly to the database or create a migration script. Example:

```python
from app import app
from models import db, Asset

with app.app_context():
    new_asset = Asset(
        ticker='NEW',
        classification='Stock',  # or 'ETF' or 'Crypto'
        quantity=100.0,
        price_paid=50.00,
        location='Etrade',  # or 'Coinbase' or 'Hard Wallet'
        company_name='New Company Inc.'
    )
    db.session.add(new_asset)
    db.session.commit()
```

## Contributing

This is a personal finance tracker. Modify as needed for your use case.

## License

Private use only.
