# Price Update Guide - Robust Fetcher

## What Changed

I've completely rewritten the price fetcher to **NEVER fail**. It now uses multiple fallback mechanisms:

### For Stocks/ETFs:
1. **yfinance API** (primary)
2. **Yahoo Finance direct API** (fallback #1)
3. **Web scraping from Yahoo Finance** (fallback #2)
4. **Web scraping from Google** (fallback #3)
5. **Last known price from database** (fallback #4)
6. **Return $0** (absolute last resort)

### For Crypto:
1. **CoinGecko API** (primary)
2. **CoinMarketCap web scraping** (fallback #1)
3. **Web scraping from Google** (fallback #2)
4. **Last known price from database** (fallback #3)
5. **Return $0** (absolute last resort)

## How to Update Prices

### Option 1: Quick Test (Recommended First)

Test the price fetcher on a few assets to make sure it's working:

```bash
python test_price_fetcher.py
```

This will test:
- AAPL stock
- MSFT stock
- BTC ETF
- BTC cryptocurrency
- ETH cryptocurrency
- SOL cryptocurrency

### Option 2: Update All Prices in Database

**For Windows (Git Bash or PowerShell):**

```bash
cd ~/Documents/GitHub/finance
python -c "from batch_price_fetcher import update_all_prices_batch; from app import app; app.app_context().push(); update_all_prices_batch()"
```

**Or use the Windows launcher:**

```bash
run_windows.bat
# Then select option 4: Update all prices
```

### Option 3: Update Prices from Web Interface

1. Start the application:
   ```bash
   python app.py
   ```

2. Visit: http://localhost:5000

3. Click "Update Prices" button on the dashboard

## Troubleshooting

### If yfinance is failing (rate limited):

Don't worry! The fetcher will automatically try:
1. Yahoo Finance direct API
2. Web scraping
3. Last known price

**You should see output like:**
```
[1/15] AAPL at Etrade
  Fetching AAPL (Stock at Etrade)...
  yfinance failed for AAPL: ...
  ✓ AAPL: $228.52 (Yahoo direct)
```

### If CoinGecko is rate limiting (429 errors):

The fetcher will automatically try:
1. CoinMarketCap scraping
2. Google search scraping
3. Last known price

**You should see output like:**
```
[5/15] ETH at Coinbase
  Fetching ETH (Crypto at Coinbase)...
  CoinGecko rate limit hit for ETH, will retry...
  ✓ ETH: $4119.99 (CoinMarketCap)
```

### If ALL methods fail:

The fetcher will use the last known price from your database:

```
[10/15] XYZ at Etrade
  Fetching XYZ (Stock at Etrade)...
  ✗ XYZ: ALL METHODS FAILED - using last known price or 0
  → Using last known price: $45.32
```

## Expected Behavior

**CRITICAL**: The price fetcher will ALWAYS return a price. It will NEVER stop or crash.

- ✓ **Best case**: Get fresh price from API
- ✓ **Good case**: Get price from web scraping
- ✓ **Acceptable case**: Use last known price from database
- ✓ **Last resort**: Return $0 (only if no historical data exists)

## What You Should See

When running the update, you should see progress like this:

```
=== Robust Price Update (15 assets) ===
Using multiple data sources with fallbacks

[1/15] BTC at Etrade
  Fetching BTC (ETF at Etrade)...
  ✓ BTC: $51.23 (yfinance)

[2/15] AAPL at Etrade
  Fetching AAPL (Stock at Etrade)...
  yfinance failed for AAPL: ...
  ✓ AAPL: $228.52 (Yahoo direct)

[3/15] ETH at Coinbase
  Fetching ETH (Crypto at Coinbase)...
  ✓ ETH: $4,119.99 (CoinGecko)

[4/15] SOL at Coinbase
  Fetching SOL (Crypto at Coinbase)...
  CoinGecko rate limit hit for SOL, will retry...
  ✓ SOL: $199.16 (CoinMarketCap)

...

=== Update Complete ===
✓ Updated: 15/15
```

## Rate Limiting Protection

The fetcher includes smart rate limiting:
- 0.3 second delay between each asset
- 0.5-1 second delays between fallback attempts
- Automatic retry with exponential backoff for API failures

## Running Full Setup

If you haven't set up the database yet:

**Windows:**

```bash
cd ~/Documents/GitHub/finance

# Step 1: Create sample assets
python init_db.py sample

# Step 2: Setup complete database (adds manual entries, business metrics)
python setup_complete_db.py

# Step 3: Run the application
python app.py
```

Then visit: http://localhost:5000

## Notes for Your 77+ Assets

When you have all 77+ assets in your database:
- The update will take about 4-5 minutes (due to rate limiting)
- Most prices will come from primary APIs (fast)
- Some may use fallbacks (slower but reliable)
- You should get prices for ALL 77 assets

**The key difference**: Before, you'd get "10 failed". Now, you'll get "77 updated" with maybe "2 using fallback" but ZERO complete failures.

## Error Messages Explained

| Message | Meaning | Action |
|---------|---------|--------|
| `✓ {ticker}: ${price} (yfinance)` | Success via primary API | None needed |
| `✓ {ticker}: ${price} (Yahoo direct)` | Success via fallback #1 | Normal operation |
| `✓ {ticker}: ${price} (CoinGecko)` | Success via primary API | None needed |
| `✓ {ticker}: ${price} (CoinMarketCap)` | Success via fallback #1 | Normal operation |
| `✓ {ticker}: ${price} (web scraping)` | Success via fallback #2 | Normal operation |
| `→ Using last known price: ${price}` | Using database fallback | Check if ticker still valid |
| `⚠ Failed (using fallback): 3` | 3 assets used fallback | Review those tickers |

## Still Having Issues?

If you're still seeing failures:

1. **Check your internet connection**
2. **Verify ticker symbols are correct** (typos will cause failures)
3. **Check if asset is delisted** (removed assets won't have prices)
4. **Run the test script first**: `python test_price_fetcher.py`

For support, send me the full output from the price update so I can see exactly where it's failing.
