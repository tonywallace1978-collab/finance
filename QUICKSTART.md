# Quick Start Guide - Financial Tracker

## What Was Built

A **complete financial tracking system** that shows your entire financial picture in one place:

✅ **Investment Portfolio Tracking** (77+ assets)
- E*Trade stocks and ETFs
- Coinbase crypto
- Hard Wallet crypto
- Automatic price updates with batch fetching

✅ **Manual Entry Management**
- 401K accounts (Tony, Heather)
- Cash holdings
- Credit cards (liabilities)
- Property and other assets

✅ **Business Metrics**
- Contractor count
- Monthly revenue
- Monthly burn rate
- Runway calculation

✅ **Special BTC Handling**
- BTC ticker correctly differentiates between:
  - BTC ETF in E*Trade (~$51)
  - Actual Bitcoin in Hard Wallet/Coinbase (~$115k)

## Files Created/Updated

### Core Application
- **`app.py`** - Main Flask application with all routes
- **`models.py`** - Database models (Asset, AssetPrice, ManualEntry, BusinessMetrics, Expense)
- **`batch_price_fetcher.py`** - Efficient batch price fetching for 77+ assets

### Templates
- **`templates/dashboard_complete.html`** - Main dashboard with complete financial overview
- **`templates/manual_entries.html`** - Edit manual entries (401K, cash, etc.)
- **`templates/business.html`** - Business metrics dashboard with charts
- **`templates/portfolio.html`** - Updated for complete portfolio view
- **`templates/stocks.html`** - E*Trade view (existing)
- **`templates/crypto_coinbase.html`** - Coinbase view (existing)
- **`templates/crypto_l.html`** - Hard Wallet view (existing)

### Setup & Documentation
- **`setup_complete_db.py`** - Complete database setup script
- **`README.md`** - Updated with complete documentation
- **`QUICKSTART.md`** - This file

## Getting Started (3 Steps)

### Step 1: Setup Database

If you have an **existing** finance.db with your assets:

```bash
cd ~/Documents/GitHub/finance
python setup_complete_db.py
```

If you want to **test with sample data** first:

```bash
cd ~/Documents/GitHub/finance
python init_db.py sample
python setup_complete_db.py
```

### Step 2: Run the Application

```bash
python app.py
```

You should see:
```
Database tables created
 * Running on http://0.0.0.0:5000
```

### Step 3: Open in Browser

Visit: **http://localhost:5000**

You'll see the complete dashboard with:
- Total Net Worth (big number at top)
- Investment accounts (E*Trade, Coinbase, Hard Wallet)
- Manual entries (401K, Cash, Credit Cards)
- Business metrics (Contractors, Revenue, Burn)

## Configuring Your Data

### Update Manual Entries

1. Click "Manual Entries" in the navigation
2. Click "Edit" on any entry
3. Update the value to match your actual finances
4. Click "Save Changes"

Sample entries to update:
- Tony 401K: Current balance
- Heather 401K: Current balance
- Bank Accounts: Total cash
- Credit Cards: Current balances

### Update Business Metrics

1. Click "Business Metrics" in the navigation
2. Add new records as your business changes
3. Track: Number of contractors, monthly revenue, monthly burn

### Update Investment Prices

Click "Update Prices" in the navigation to fetch latest prices for all 77+ assets.

This uses **batch fetching**:
- All crypto prices in 1-2 API calls (efficient!)
- Stock prices with rate limiting
- BTC handled correctly based on location

## How Net Worth is Calculated

```
Assets:
  + Investment Portfolio Value (all 77+ assets)
  + 401K Accounts (Tony + Heather)
  + Cash Holdings
  + Property

Liabilities:
  - Debt
  - Credit Cards

= Total Net Worth
```

Expected total: **~$1,595,000** with your data

## Key Features to Try

### 1. Complete Dashboard
- Shows everything in one view
- Real-time calculations
- Visual cards for each account type

### 2. Location-Specific Views
- `/stocks` - E*Trade only
- `/crypto-coinbase` - Coinbase only
- `/crypto-l` - Hard Wallet only
- Each shows: Total value, gain/loss, day change

### 3. Full Portfolio View
- `/portfolio` - All assets across all locations
- Sorted by value
- Shows which location each asset is in

### 4. Live Editing
- Click on any manual entry value to edit it
- Changes reflect immediately in net worth
- Tracks who updated it and when

### 5. Business Dashboard
- Visualize revenue vs burn over time
- Calculate runway based on current metrics
- Track contractor count

## Troubleshooting

### Prices not updating?
```bash
python -c "from batch_price_fetcher import update_all_prices_batch; update_all_prices_batch()"
```

### Database issues?
```bash
# Backup first!
cp instance/finance.db instance/finance.db.backup

# Then recreate tables
python setup_complete_db.py
```

### Wrong BTC price showing?
Check that:
1. BTC in E*Trade has `location='Etrade'` (shows ETF price ~$51)
2. BTC in Hard Wallet has `location='Hard Wallet'` (shows Bitcoin price ~$115k)

The `location` field is critical for BTC differentiation.

## What's Different from Before?

### Before (Old Version)
- ❌ Only showed investment accounts
- ❌ Missing 401K, cash, debt tracking
- ❌ No business metrics
- ❌ Slow price updates (77 individual API calls)
- ❌ No manual entry editing

### Now (Complete Version)
- ✅ Complete financial picture
- ✅ Manual entries for all assets/liabilities
- ✅ Business performance tracking
- ✅ Batch price updates (1-2 API calls for all crypto)
- ✅ Live editing of all values
- ✅ Professional dashboard with charts

## Next Steps

1. **Customize manual entries** to match your actual finances
2. **Add business metrics** if you track contractor work
3. **Set up automatic price updates** (future: cron job or scheduled task)
4. **Export data** for tax purposes (future feature)
5. **Add more assets** as needed

## Support

- **Documentation**: See README.md
- **BTC Dual-Ticker**: See README.md section on BTC handling
- **API Documentation**: See README.md API Endpoints section

---

**You're all set!** 🎉

Run `python app.py` and visit http://localhost:5000 to see your complete financial tracker.
