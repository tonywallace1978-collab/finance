from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class Asset(db.Model):
    """Investment assets (stocks, ETFs, crypto)"""
    __tablename__ = 'asset'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False)
    classification = db.Column(db.String(50), nullable=False)  # Stock, ETF, Crypto
    company_name = db.Column(db.String(200))
    quantity = db.Column(db.Float, nullable=False)
    price_paid = db.Column(db.Float)
    location = db.Column(db.String(50), nullable=False)  # Etrade, Coinbase, Hard Wallet
    purchase_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class AssetPrice(db.Model):
    """Price tracking"""
    __tablename__ = 'asset_price'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    change_dollar = db.Column(db.Float)
    change_percent = db.Column(db.Float)
    location = db.Column(db.String(50))  # For BTC differentiation
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class ManualEntry(db.Model):
    """Manual entries (401k, Cash, Property, Debt)"""
    __tablename__ = 'manual_entry'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))  # 401K, Cash, Property, Debt, Credit Card
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(50), default='Manual')

class BusinessMetrics(db.Model):
    """Business tracking"""
    __tablename__ = 'business_metrics'

    id = db.Column(db.Integer, primary_key=True)
    contractors_working = db.Column(db.Integer)
    monthly_revenue = db.Column(db.Float)
    monthly_burn = db.Column(db.Float, default=20000)
    date = db.Column(db.Date, default=datetime.utcnow)
    updated_by = db.Column(db.String(50))

class Expense(db.Model):
    """Monthly expense tracking"""
    __tablename__ = 'expense'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_business = db.Column(db.Boolean, default=False)

# ==================== HELPER FUNCTIONS ====================

def calculate_investment_value():
    """Calculate total value of all investments"""
    total = 0
    for asset in Asset.query.all():
        latest_price = AssetPrice.query.filter_by(
            ticker=asset.ticker,
            location=asset.location
        ).order_by(AssetPrice.timestamp.desc()).first()

        if latest_price and asset.quantity:
            total += latest_price.price * asset.quantity
    return total

def calculate_manual_totals():
    """Calculate totals from manual entries"""
    totals = {}
    for entry in ManualEntry.query.all():
        if entry.category not in totals:
            totals[entry.category] = 0
        totals[entry.category] += entry.value
    return totals

def get_net_worth():
    """Calculate total net worth"""
    investments = calculate_investment_value()
    manual_totals = calculate_manual_totals()

    assets = investments
    assets += manual_totals.get('401K', 0)
    assets += manual_totals.get('Cash', 0)
    assets += manual_totals.get('Property', 0)

    liabilities = manual_totals.get('Debt', 0)
    liabilities += manual_totals.get('Credit Card', 0)

    return assets - liabilities

def get_location_summary(location):
    """Get summary for specific location"""
    assets = Asset.query.filter_by(location=location).all()

    total_value = 0
    total_cost_basis = 0
    day_change_dollar = 0
    asset_details = []

    for asset in assets:
        price_data = AssetPrice.query.filter_by(
            ticker=asset.ticker,
            location=asset.location
        ).order_by(AssetPrice.timestamp.desc()).first()

        if price_data and asset.quantity:
            current_value = price_data.price * asset.quantity
            cost_basis = (asset.price_paid or 0) * asset.quantity
            total_gain_dollar = current_value - cost_basis if cost_basis > 0 else 0
            day_change_for_asset = (price_data.change_dollar or 0) * asset.quantity

            total_value += current_value
            total_cost_basis += cost_basis
            day_change_dollar += day_change_for_asset

            # Structure matches template expectations
            asset_details.append({
                'asset': asset,  # Full asset object for template
                'current_price': price_data.price,
                'current_value': current_value,
                'day_change_dollar': day_change_for_asset,
                'day_change_percent': price_data.change_percent or 0,
                'total_gain_dollar': total_gain_dollar,
                'total_gain_percent': (total_gain_dollar / cost_basis * 100) if cost_basis > 0 else 0
            })

    total_gain_dollar = total_value - total_cost_basis

    return {
        'location': location,
        'total_value': total_value,
        'total_cost_basis': total_cost_basis,
        'total_gain': total_gain_dollar,
        'total_gain_dollar': total_gain_dollar,
        'total_gain_percent': (total_gain_dollar / total_cost_basis * 100) if total_cost_basis > 0 else 0,
        'day_change_dollar': day_change_dollar,
        'assets': asset_details,
        'asset_count': len(assets)
    }

# ==================== ROUTES ====================

@app.route('/')
def dashboard():
    """Main dashboard"""
    # Investment summaries
    etrade = get_location_summary('Etrade')
    coinbase = get_location_summary('Coinbase')
    hardwallet = get_location_summary('Hard Wallet')

    # Manual entries
    manual_totals = calculate_manual_totals()

    # Business metrics
    latest_business = BusinessMetrics.query.order_by(BusinessMetrics.date.desc()).first()

    # Net worth
    net_worth = get_net_worth()

    # Last update time
    last_price = AssetPrice.query.order_by(AssetPrice.timestamp.desc()).first()
    last_update = last_price.timestamp if last_price else None

    return render_template('dashboard_complete.html',
                         net_worth=net_worth,
                         etrade=etrade,
                         coinbase=coinbase,
                         hardwallet=hardwallet,
                         manual_totals=manual_totals,
                         business=latest_business,
                         last_update=last_update)

@app.route('/portfolio')
def portfolio():
    """Complete portfolio view"""
    all_assets = []
    total_value = 0
    total_cost_basis = 0

    for asset in Asset.query.all():
        price_data = AssetPrice.query.filter_by(
            ticker=asset.ticker,
            location=asset.location
        ).order_by(AssetPrice.timestamp.desc()).first()

        if price_data:
            current_value = price_data.price * asset.quantity
            cost_basis = (asset.price_paid or 0) * asset.quantity
            total_gain_dollar = current_value - cost_basis
            day_change_dollar = (price_data.change_dollar or 0) * asset.quantity

            total_value += current_value
            total_cost_basis += cost_basis

            all_assets.append({
                'asset': asset,
                'current_price': price_data.price,
                'current_value': current_value,
                'day_change_dollar': day_change_dollar,
                'day_change_percent': price_data.change_percent or 0,
                'total_gain_dollar': total_gain_dollar,
                'total_gain_percent': (total_gain_dollar / cost_basis * 100) if cost_basis > 0 else 0
            })

    # Sort by current value
    all_assets.sort(key=lambda x: x['current_value'], reverse=True)

    total_gain_dollar = total_value - total_cost_basis
    total_gain_percent = (total_gain_dollar / total_cost_basis * 100) if total_cost_basis > 0 else 0

    return render_template('portfolio.html',
                         assets=all_assets,
                         total_value=total_value,
                         total_cost_basis=total_cost_basis,
                         total_gain_dollar=total_gain_dollar,
                         total_gain_percent=total_gain_percent)

@app.route('/stocks')
def stocks():
    """E*Trade portfolio view"""
    summary = get_location_summary('Etrade')
    return render_template('stocks.html', summary=summary)

@app.route('/crypto-coinbase')
def crypto_coinbase():
    """Coinbase portfolio view"""
    summary = get_location_summary('Coinbase')
    return render_template('crypto_coinbase.html', summary=summary)

@app.route('/crypto-l')
def crypto_l():
    """Hard Wallet (L Wallet) portfolio view"""
    summary = get_location_summary('Hard Wallet')
    return render_template('crypto_l.html', summary=summary)

@app.route('/manual-entries')
def manual_entries():
    """View/edit manual entries"""
    entries = ManualEntry.query.all()
    return render_template('manual_entries.html', entries=entries)

@app.route('/api/manual-entry/update', methods=['POST'])
def update_manual_entry():
    """Update manual entry value"""
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
def update_prices():
    """Trigger price update"""
    from batch_price_fetcher import update_all_prices_batch

    try:
        updated, failed = update_all_prices_batch()
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
def update_prices_redirect():
    """Manual price update - redirects back to dashboard"""
    from batch_price_fetcher import update_all_prices_batch

    try:
        update_all_prices_batch()
    except Exception as e:
        print(f"Price update error: {e}")

    return redirect(url_for('dashboard'))

@app.route('/business')
def business():
    """Business metrics dashboard"""
    metrics = BusinessMetrics.query.order_by(BusinessMetrics.date.desc()).all()
    return render_template('business.html', metrics=metrics)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created")

    app.run(debug=True, host='0.0.0.0', port=5000)
