"""
Setup script for complete financial tracker database

This script:
1. Creates all database tables
2. Adds sample manual entries (401k, Cash, etc.)
3. Adds sample business metrics
4. Updates prices for existing assets

Run this after copying your existing finance.db database.
"""

from app import app, db
from models import ManualEntry, BusinessMetrics
from datetime import date

def setup_manual_entries():
    """Add sample manual entries if none exist"""
    if ManualEntry.query.count() > 0:
        print("Manual entries already exist, skipping...")
        return

    print("Adding sample manual entries...")

    # 401K Accounts
    entries = [
        ManualEntry(name='Tony 401K', value=314000, category='401K', updated_by='System'),
        ManualEntry(name='Heather 401K', value=75000, category='401K', updated_by='System'),

        # Cash
        ManualEntry(name='Bank Accounts', value=492000, category='Cash', updated_by='System'),

        # Credit Cards (liabilities - will be negative in net worth)
        # These should be positive values, the net worth calculation will subtract them
        ManualEntry(name='Credit Card 1', value=5000, category='Credit Card', updated_by='System'),
        ManualEntry(name='Credit Card 2', value=3000, category='Credit Card', updated_by='System'),
    ]

    for entry in entries:
        db.session.add(entry)

    db.session.commit()
    print(f"Added {len(entries)} manual entries")


def setup_business_metrics():
    """Add sample business metrics if none exist"""
    if BusinessMetrics.query.count() > 0:
        print("Business metrics already exist, skipping...")
        return

    print("Adding sample business metrics...")

    # Sample metrics
    metrics = [
        BusinessMetrics(
            contractors_working=5,
            monthly_revenue=45000,
            monthly_burn=20000,
            date=date.today(),
            updated_by='System'
        )
    ]

    for metric in metrics:
        db.session.add(metric)

    db.session.commit()
    print(f"Added {len(metrics)} business metric records")


def main():
    """Main setup function"""
    with app.app_context():
        print("\n=== Financial Tracker Complete Setup ===\n")

        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created\n")

        # Add sample data
        setup_manual_entries()
        print()
        setup_business_metrics()
        print()

        # Update prices
        print("Updating asset prices...")
        try:
            from batch_price_fetcher import update_all_prices_batch
            updated, failed = update_all_prices_batch()
            print(f"✓ Price update complete: {updated} updated, {failed} failed")
        except Exception as e:
            print(f"✗ Price update failed: {e}")
            print("  You can update prices manually from the web interface")

        print("\n=== Setup Complete ===")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Visit: http://localhost:5000")
        print("3. Update manual entry values in the Manual Entries page")
        print("4. Update business metrics in the Business Metrics page")
        print("\nNote: The sample manual entries are just placeholders.")
        print("Edit them to match your actual financial data.\n")


if __name__ == '__main__':
    main()
