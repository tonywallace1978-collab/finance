# Financial Tracker - Complete Financial Overview

A comprehensive Flask-based financial tracking application that provides a complete view of your net worth, including investments, retirement accounts, cash, property, debt, and business metrics.

**🚀 NEW: Deploy to Railway.app and access from anywhere! See [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)**

## Deployment Options

### Option 1: Railway.app (Recommended - Access from Anywhere)
- ✅ Free tier available ($5 credit/month)
- ✅ Secure login with username/password
- ✅ PostgreSQL database included
- ✅ HTTPS encryption automatic
- ✅ Access from any device (computer, phone, tablet)
- ✅ Auto-updates when you push to GitHub
- 📖 **[Full Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md)**

### Option 2: Local (Run on Your Computer)
- ✅ Free
- ✅ Keep data on your computer
- ✅ No internet required
- ❌ Only accessible from local computer
- 📖 See "Setup Instructions" below

## Key Features

### Investment Tracking
- **Multi-location portfolio tracking** across E*Trade, Coinbase, and Hard Wallet
- **Automatic price fetching** from yfinance (stocks/ETFs) and CoinGecko (crypto)
- **Special BTC handling** - correctly differentiates between BTC ETF and actual Bitcoin
- **Real-time portfolio valuations** with gain/loss calculations
- **77+ assets** tracked efficiently with batch API calls

### Complete Financial Picture
- **Manual entries** for 401K accounts, cash, property, debt, credit cards
- **Business metrics tracking** - contractors, revenue, burn rate, runway
- **Expense tracking** with monthly categorization
- **Complete net worth calculation** combining all financial sources
- **Responsive dashboard** with Bootstrap styling and real-time updates

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

### 2. Initialize Complete Database

**Option A: New Installation (with sample data)**
```bash
# Creates all tables and adds sample data for testing
python init_db.py sample

# Then run complete setup for manual entries and business metrics
python setup_complete_db.py
```

**Option B: Upgrade Existing Database**
```bash
# If you already have a finance.db with assets, just run complete setup
# This will add the new tables (ManualEntry, BusinessMetrics, Expense)
python setup_complete_db.py
```

**Option C: Import Your Existing Database**
```bash
# Copy your database file
cp /path/to/your/finance.db instance/finance.db

# Run complete setup to add new tables and update prices
python setup_complete_db.py
```

### 3. Configure Your Financial Data

After setup, edit the sample data to match your actual finances:

1. **Manual Entries**: Go to `/manual-entries` and update:
   - 401K account balances (Tony 401K, Heather 401K)
   - Cash holdings (Bank Accounts)
   - Credit card balances
   - Any property or other assets

2. **Business Metrics**: Go to `/business` and add records for:
   - Number of billable contractors
   - Monthly revenue
   - Monthly burn rate

### 4. Run the Application

```bash
python app.py
```

Visit: http://localhost:5000

The dashboard will show your complete net worth including all financial sources.

## Application Routes

### Main Pages
- `/` - **Dashboard** - Complete financial overview with net worth, investments, manual entries, and business metrics
- `/stocks` - **E*Trade Portfolio** - Stock and ETF holdings with current prices and gains
- `/crypto-coinbase` - **Coinbase Portfolio** - Cryptocurrency holdings on Coinbase
- `/crypto-l` - **Hard Wallet Portfolio** - Cold storage crypto holdings (L Wallet)
- `/portfolio` - **Complete Portfolio** - All investments across all locations in one view
- `/manual-entries` - **Manual Entries** - Edit 401K, cash, debt, and other manual entries
- `/business` - **Business Metrics** - Track contractors, revenue, burn rate, and runway

### API Endpoints
- `POST /api/update-prices` - Trigger batch price update for all assets
- `POST /api/manual-entry/update` - Update a manual entry value
- `GET /api/assets` - Get all assets as JSON
- `GET /api/prices/<ticker>/<location>` - Get latest price for specific asset

### Utility Routes
- `/update-prices` - Manually trigger price update (redirects to dashboard)

## Database Schema

### Asset Table
Stores investment assets (stocks, ETFs, cryptocurrencies)
```sql
- id (Primary Key)
- ticker (e.g., 'BTC', 'AAPL')
- classification (Stock, ETF, Crypto)
- quantity (shares/coins)
- price_paid (average cost basis)
- location (Etrade, Coinbase, Hard Wallet)
- company_name (optional)
- purchase_date (optional)
- notes (optional)
- last_updated (timestamp)
```

### AssetPrice Table
Historical price tracking with location awareness
```sql
- id (Primary Key)
- ticker
- price
- change_dollar (daily change)
- change_percent (daily change %)
- timestamp (indexed)
- location (crucial for BTC differentiation)
```

### ManualEntry Table
Non-tradeable assets and liabilities
```sql
- id (Primary Key)
- name (e.g., "Tony 401K", "Bank Account")
- value (current value)
- category (401K, Cash, Property, Debt, Credit Card)
- last_updated (timestamp)
- updated_by (who updated it)
```

### BusinessMetrics Table
Business performance tracking
```sql
- id (Primary Key)
- contractors_working (number of billable contractors)
- monthly_revenue (current monthly revenue)
- monthly_burn (monthly expenses, default 20000)
- date (date of metric)
- updated_by (who updated it)
```

### Expense Table
Monthly expense tracking (future feature)
```sql
- id (Primary Key)
- date (expense date)
- amount (expense amount)
- category (expense category)
- description (optional notes)
- is_business (boolean, business vs personal)
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

## Expected Financial Overview

Based on your complete financial data, the application should show approximately:

### Investment Accounts
- **E*Trade**: ~$590,000 (stocks, ETFs, BTC ETF)
- **Coinbase**: ~$92,000 (cryptocurrencies)
- **Hard Wallet**: ~$479,000 (cold storage crypto including actual Bitcoin)
- **Total Investments**: ~$1,161,000

### Manual Entries
- **401K Accounts**: ~$389,000 (Tony + Heather)
- **Cash**: ~$492,000 (bank accounts)
- **Credit Cards**: Variable (liabilities)

### Complete Net Worth
**Total Net Worth**: ~$1,595,000 (investments + 401K + cash - liabilities)

This includes all financial sources and represents your complete financial picture.

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
