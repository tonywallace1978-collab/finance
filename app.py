from flask import Flask, render_template, jsonify, redirect, url_for
from models import db, Asset, AssetPrice
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
        'total_gain_dollar': total_gain,
        'total_gain_percent': total_gain_percent,
        'day_change_dollar': total_day_change,
        'day_change_percent': (total_day_change / total_cost_basis * 100) if total_cost_basis > 0 else 0,
        'assets': asset_details,
        'asset_count': len(assets)
    }


@app.route('/')
def dashboard():
    """Main dashboard showing overview of all locations"""

    # Get summaries for each location
    etrade_summary = get_location_summary('Etrade')
    coinbase_summary = get_location_summary('Coinbase')
    hardwallet_summary = get_location_summary('Hard Wallet')

    # Calculate total net worth
    total_net_worth = (
        etrade_summary['total_value'] +
        coinbase_summary['total_value'] +
        hardwallet_summary['total_value']
    )

    total_day_change = (
        etrade_summary['day_change_dollar'] +
        coinbase_summary['day_change_dollar'] +
        hardwallet_summary['day_change_dollar']
    )

    total_cost_basis = (
        etrade_summary['total_cost_basis'] +
        coinbase_summary['total_cost_basis'] +
        hardwallet_summary['total_cost_basis']
    )

    total_gain = total_net_worth - total_cost_basis
    total_gain_percent = (total_gain / total_cost_basis * 100) if total_cost_basis > 0 else 0

    # Get last update time
    last_price_update = AssetPrice.query.order_by(AssetPrice.timestamp.desc()).first()
    last_update = last_price_update.timestamp if last_price_update else None

    return render_template('dashboard.html',
                           total_net_worth=total_net_worth,
                           total_day_change=total_day_change,
                           total_gain_dollar=total_gain,
                           total_gain_percent=total_gain_percent,
                           etrade=etrade_summary,
                           coinbase=coinbase_summary,
                           hardwallet=hardwallet_summary,
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


@app.route('/update-prices')
def update_prices():
    """Manually trigger price update for all assets"""
    assets = Asset.query.all()
    updated, failed = price_fetcher.update_all_prices(assets)

    return jsonify({
        'success': True,
        'updated': updated,
        'failed': failed,
        'timestamp': datetime.utcnow().isoformat()
    })


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
