"""
Database initialization script for Financial Tracker

This script creates the database tables and can populate them with sample data.
Run this before starting the application for the first time.
"""

from app import app
from models import db, Asset, AssetPrice
from price_fetcher import PriceFetcher

def init_database():
    """Initialize the database tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

def add_sample_data():
    """Add sample data to test the application"""
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        AssetPrice.query.delete()
        Asset.query.delete()
        db.session.commit()

        print("Adding sample assets...")

        # E*Trade Sample Assets (Stocks and ETFs)
        etrade_assets = [
            # BTC ETF in E*Trade (Grayscale Bitcoin Mini Trust)
            Asset(ticker='BTC', classification='ETF', quantity=102.4,
                  price_paid=45.00, location='Etrade',
                  company_name='Grayscale Bitcoin Mini Trust ETF'),
            Asset(ticker='AAPL', classification='Stock', quantity=50.0,
                  price_paid=150.00, location='Etrade',
                  company_name='Apple Inc.'),
            Asset(ticker='MSFT', classification='Stock', quantity=30.0,
                  price_paid=300.00, location='Etrade',
                  company_name='Microsoft Corporation'),
            Asset(ticker='GOOGL', classification='Stock', quantity=20.0,
                  price_paid=120.00, location='Etrade',
                  company_name='Alphabet Inc.'),
            Asset(ticker='TSLA', classification='Stock', quantity=15.0,
                  price_paid=200.00, location='Etrade',
                  company_name='Tesla Inc.'),
            Asset(ticker='SPY', classification='ETF', quantity=100.0,
                  price_paid=400.00, location='Etrade',
                  company_name='SPDR S&P 500 ETF Trust'),
        ]

        # Coinbase Sample Assets (Crypto)
        coinbase_assets = [
            Asset(ticker='ETH', classification='Crypto', quantity=5.5,
                  price_paid=2000.00, location='Coinbase',
                  company_name='Ethereum'),
            Asset(ticker='SOL', classification='Crypto', quantity=100.0,
                  price_paid=80.00, location='Coinbase',
                  company_name='Solana'),
            Asset(ticker='ADA', classification='Crypto', quantity=10000.0,
                  price_paid=0.40, location='Coinbase',
                  company_name='Cardano'),
            Asset(ticker='LINK', classification='Crypto', quantity=500.0,
                  price_paid=15.00, location='Coinbase',
                  company_name='Chainlink'),
        ]

        # Hard Wallet Sample Assets (Crypto)
        hardwallet_assets = [
            # BTC Crypto in Hard Wallet (Actual Bitcoin)
            Asset(ticker='BTC', classification='Crypto', quantity=1.534908,
                  price_paid=45000.00, location='Hard Wallet',
                  company_name='Bitcoin'),
            Asset(ticker='ETH', classification='Crypto', quantity=10.0,
                  price_paid=1800.00, location='Hard Wallet',
                  company_name='Ethereum'),
            Asset(ticker='COMP', classification='Crypto', quantity=50.0,
                  price_paid=120.00, location='Hard Wallet',
                  company_name='Compound'),
            Asset(ticker='HBAR', classification='Crypto', quantity=20000.0,
                  price_paid=0.10, location='Hard Wallet',
                  company_name='Hedera'),
            Asset(ticker='PAXG', classification='Crypto', quantity=2.0,
                  price_paid=1900.00, location='Hard Wallet',
                  company_name='PAX Gold'),
        ]

        # Add all assets to database
        all_assets = etrade_assets + coinbase_assets + hardwallet_assets
        for asset in all_assets:
            db.session.add(asset)

        db.session.commit()
        print(f"Added {len(all_assets)} sample assets:")
        print(f"  - E*Trade: {len(etrade_assets)} assets")
        print(f"  - Coinbase: {len(coinbase_assets)} assets")
        print(f"  - Hard Wallet: {len(hardwallet_assets)} assets")

        # Fetch prices for all assets
        print("\nFetching prices for all assets...")
        price_fetcher = PriceFetcher()
        updated, failed = price_fetcher.update_all_prices(all_assets)

        print(f"\nDatabase initialized successfully!")
        print(f"Assets: {len(all_assets)}")
        print(f"Prices updated: {updated}")
        print(f"Prices failed: {failed}")

def import_from_user_db():
    """
    Instructions for importing from your existing database:

    1. Copy your finance.db file to the instance/ directory
    2. Make sure it has the correct schema (Asset and AssetPrice tables)
    3. Run the price update: python -c "from init_db import update_prices; update_prices()"
    """
    print("\nTo import your existing database:")
    print("1. Copy your finance.db file to: instance/finance.db")
    print("2. Update prices: python -c \"from init_db import update_prices; update_prices()\"")

def update_prices():
    """Update prices for all assets in the database"""
    with app.app_context():
        assets = Asset.query.all()
        print(f"Updating prices for {len(assets)} assets...")

        price_fetcher = PriceFetcher()
        updated, failed = price_fetcher.update_all_prices(assets)

        print(f"\nPrice update complete!")
        print(f"Updated: {updated}")
        print(f"Failed: {failed}")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'init':
            init_database()
        elif command == 'sample':
            init_database()
            add_sample_data()
        elif command == 'update-prices':
            update_prices()
        elif command == 'import-help':
            import_from_user_db()
        else:
            print("Unknown command. Available commands:")
            print("  init          - Create database tables only")
            print("  sample        - Create tables and add sample data")
            print("  update-prices - Update prices for existing assets")
            print("  import-help   - Show instructions for importing your database")
    else:
        print("Financial Tracker - Database Initialization")
        print("\nUsage: python init_db.py [command]")
        print("\nCommands:")
        print("  init          - Create database tables only")
        print("  sample        - Create tables and add sample data")
        print("  update-prices - Update prices for existing assets")
        print("  import-help   - Show instructions for importing your database")
