from flask import Flask, render_template, jsonify, redirect, url_for, request
from models import db, Asset, AssetPrice, ManualEntry, BusinessMetrics, Expense
from price_fetcher import PriceFetcher
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Initialize database
db.init_app(app)

# Initialize price fetcher
price_fetcher = PriceFetcher()


def calculate_asset_value(asset, price_data):
    """Calculate current value and gains for an asset"""
    if not price_data:
        return None

    current_value = asset.quantity * price_data.price
    cost_basis = asset.quantity * asset.price_paid
    total_gain_dollar = current_value - cost_basis
    total_gain_percent = (total_gain_dollar / cost_basis * 100) if cost_basis > 0 else 0

    return {
        'asset': asset,
        'current_price': price_data.price,
        'current_value': current_value,
        'cost_basis': cost_basis,
        'total_gain_dollar': total_gain_dollar,
        'total_gain_percent': total_gain_percent,
        'day_change_dollar': price_data.change_dollar * asset.quantity if price_data.change_dollar else 0,
        'day_change_percent': price_data.change_percent if price_data.change_percent else 0
    }


def get_location_summary(location):
    """Get summary statistics for a specific location"""
    assets = Asset.query.filter_by(location=location).all()

    total_value = 0
    total_cost_basis = 0
    total_day_change = 0
    asset_details = []

    for asset in assets:
        price_data = price_fetcher.get_latest_price(asset.ticker, asset.location)
        if price_data:
            asset_calc = calculate_asset_value(asset, price_data)
            if asset_calc:
                total_value += asset_calc['current_value']
                total_cost_basis += asset_calc['cost_basis']
                total_day_change += asset_calc['day_change_dollar']
                asset_details.append(asset_calc)

    total_gain = total_value - total_cost_basis
    total_gain_percent = (total_gain / total_cost_basis * 100) if total_cost_basis > 0 else 0

    return {
        'location': location,
        'total_value': total_value,
        'total_cost_basis': total_cost_basis,
        'total_gain': total_gain,
        'total_gain_dollar': total_gain,
        'total_gain_percent': total_gain_percent,
        'day_change_dollar': total_day_change,
        'day_change_percent': (total_day_change / total_cost_basis * 100) if total_cost_basis > 0 else 0,
        'assets': asset_details,
        'asset_count': len(assets)
    }


def calculate_investment_value():
    """Calculate total value of all investments"""
    total = 0
    for asset in Asset.query.all():
        price_data = price_fetcher.get_latest_price(asset.ticker, asset.location)
        if price_data and asset.quantity:
            total += price_data.price * asset.quantity
    return total


def calculate_manual_totals():
    """Calculate totals from manual entries by category"""
    totals = {}
    for entry in ManualEntry.query.all():
        if entry.category not in totals:
            totals[entry.category] = 0
        totals[entry.category] += entry.value
    return totals


def get_net_worth():
    """Calculate total net worth including investments and manual entries"""
    investments = calculate_investment_value()
    manual_totals = calculate_manual_totals()

    # Assets
    assets = investments
    assets += manual_totals.get('401K', 0)
    assets += manual_totals.get('Cash', 0)
    assets += manual_totals.get('Property', 0)

    # Liabilities
    liabilities = manual_totals.get('Debt', 0)
    liabilities += manual_totals.get('Credit Card', 0)

    return assets - liabilities


@app.route('/')
def dashboard():
    """Main dashboard showing complete financial overview"""

    # Get investment summaries for each location
    etrade_summary = get_location_summary('Etrade')
    coinbase_summary = get_location_summary('Coinbase')
    hardwallet_summary = get_location_summary('Hard Wallet')

    # Get manual entries totals
    manual_totals = calculate_manual_totals()

    # Get business metrics
    latest_business = BusinessMetrics.query.order_by(BusinessMetrics.date.desc()).first()

    # Calculate complete net worth (investments + manual entries - liabilities)
    net_worth = get_net_worth()

    # Get last update time
    last_price_update = AssetPrice.query.order_by(AssetPrice.timestamp.desc()).first()
    last_update = last_price_update.timestamp if last_price_update else None

    return render_template('dashboard_complete.html',
                           net_worth=net_worth,
                           etrade=etrade_summary,
                           coinbase=coinbase_summary,
                           hardwallet=hardwallet_summary,
                           manual_totals=manual_totals,
                           business=latest_business,
                           last_update=last_update)


@app.route('/stocks')
def stocks():
    """E*Trade stocks and ETFs page"""
    summary = get_location_summary('Etrade')
    return render_template('stocks.html', summary=summary)


@app.route('/crypto-coinbase')
def crypto_coinbase():
    """Coinbase crypto holdings page"""
    summary = get_location_summary('Coinbase')
    return render_template('crypto_coinbase.html', summary=summary)


@app.route('/crypto-l')
def crypto_l():
    """Hard Wallet (L Wallet) crypto holdings page"""
    summary = get_location_summary('Hard Wallet')
    return render_template('crypto_l.html', summary=summary)


@app.route('/portfolio')
def portfolio():
    """All assets across all locations"""
    assets = Asset.query.all()

    all_assets = []
    for asset in assets:
        price_data = price_fetcher.get_latest_price(asset.ticker, asset.location)
        if price_data:
            asset_calc = calculate_asset_value(asset, price_data)
            if asset_calc:
                all_assets.append(asset_calc)

    # Sort by current value (largest first)
    all_assets.sort(key=lambda x: x['current_value'], reverse=True)

    # Calculate totals
    total_value = sum(a['current_value'] for a in all_assets)
    total_cost_basis = sum(a['cost_basis'] for a in all_assets)
    total_gain = total_value - total_cost_basis
    total_gain_percent = (total_gain / total_cost_basis * 100) if total_cost_basis > 0 else 0

    return render_template('portfolio.html',
                           assets=all_assets,
                           total_value=total_value,
                           total_cost_basis=total_cost_basis,
                           total_gain_dollar=total_gain,
                           total_gain_percent=total_gain_percent)


@app.route('/manual-entries')
def manual_entries():
    """View and edit manual entries"""
    entries = ManualEntry.query.all()
    return render_template('manual_entries.html', entries=entries)


@app.route('/business')
def business():
    """Business metrics dashboard"""
    metrics = BusinessMetrics.query.order_by(BusinessMetrics.date.desc()).all()
    return render_template('business.html', metrics=metrics)


@app.route('/api/manual-entry/update', methods=['POST'])
def update_manual_entry():
    """API endpoint to update manual entry value"""
    data = request.json
    entry = ManualEntry.query.get(data['id'])

    if entry:
        entry.value = float(data['value'])
        entry.last_updated = datetime.utcnow()
        entry.updated_by = data.get('user', 'Manual')
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Entry not found'})


@app.route('/api/update-prices', methods=['POST'])
def api_update_prices():
    """API endpoint to trigger price update"""
    try:
        # Try batch price fetcher first (more efficient)
        try:
            from batch_price_fetcher import update_all_prices_batch
            updated, failed = update_all_prices_batch()
        except ImportError:
            # Fall back to regular price fetcher
            assets = Asset.query.all()
            updated, failed = price_fetcher.update_all_prices(assets)

        return jsonify({
            'success': True,
            'updated': updated,
            'failed': failed
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/update-prices')
def update_prices():
    """Manually trigger price update for all assets (GET request)"""
    try:
        # Try batch price fetcher first (more efficient)
        try:
            from batch_price_fetcher import update_all_prices_batch
            update_all_prices_batch()
        except ImportError:
            # Fall back to regular price fetcher
            assets = Asset.query.all()
            price_fetcher.update_all_prices(assets)
    except Exception as e:
        print(f"Price update error: {e}")

    return redirect(url_for('dashboard'))


@app.route('/api/assets')
def api_assets():
    """API endpoint to get all assets"""
    assets = Asset.query.all()
    return jsonify([asset.to_dict() for asset in assets])


@app.route('/api/prices/<ticker>/<location>')
def api_price(ticker, location):
    """API endpoint to get latest price for a ticker at a location"""
    price = price_fetcher.get_latest_price(ticker, location)
    if price:
        return jsonify(price.to_dict())
    return jsonify({'error': 'Price not found'}), 404


if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("Database tables created")

    app.run(debug=True, host='0.0.0.0', port=5000)
