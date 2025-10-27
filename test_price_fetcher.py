"""
Test script for the robust price fetcher

This script tests the price fetcher on a few sample assets to verify
all fallback mechanisms work correctly.
"""

from batch_price_fetcher import RobustPriceFetcher

def test_fetcher():
    print("=== Testing Robust Price Fetcher ===\n")

    fetcher = RobustPriceFetcher()

    # Test cases
    test_cases = [
        ('AAPL', 'Stock', 'Etrade'),
        ('MSFT', 'Stock', 'Etrade'),
        ('BTC', 'ETF', 'Etrade'),  # BTC ETF
        ('BTC', 'Crypto', 'Hard Wallet'),  # Actual Bitcoin
        ('ETH', 'Crypto', 'Coinbase'),
        ('SOL', 'Crypto', 'Coinbase'),
    ]

    print("Testing price fetching with multiple fallbacks:\n")

    success_count = 0
    for ticker, classification, location in test_cases:
        print(f"\nTesting: {ticker} ({classification} at {location})")
        print("-" * 50)

        result = fetcher.fetch_price_with_fallbacks(ticker, classification, location)

        if result and result['price'] > 0:
            print(f"✓ SUCCESS: ${result['price']:,.2f}")
            success_count += 1
        else:
            print(f"✗ FAILED: Got price = {result['price'] if result else 'None'}")

    print("\n" + "=" * 50)
    print(f"Results: {success_count}/{len(test_cases)} successful")

    if success_count == len(test_cases):
        print("✓ All tests passed!")
    else:
        print(f"⚠ {len(test_cases) - success_count} tests failed")

    print("\nFailed tickers:", fetcher.failed_tickers if fetcher.failed_tickers else "None")

if __name__ == '__main__':
    test_fetcher()
