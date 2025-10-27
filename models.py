from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Asset(db.Model):
    """Asset model representing stocks, ETFs, and cryptocurrencies"""
    __tablename__ = 'asset'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False)
    classification = db.Column(db.String(50), nullable=False)  # Stock, ETF, Crypto
    quantity = db.Column(db.Float, nullable=False)
    price_paid = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(50), nullable=False)  # Etrade, Coinbase, Hard Wallet
    company_name = db.Column(db.String(200))

    def __repr__(self):
        return f'<Asset {self.ticker} at {self.location}>'

    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'classification': self.classification,
            'quantity': self.quantity,
            'price_paid': self.price_paid,
            'location': self.location,
            'company_name': self.company_name
        }


class AssetPrice(db.Model):
    """Asset price tracking with historical data"""
    __tablename__ = 'asset_price'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    change_dollar = db.Column(db.Float)
    change_percent = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    location = db.Column(db.String(50))  # Important for BTC differentiation

    def __repr__(self):
        return f'<AssetPrice {self.ticker} ${self.price} @ {self.timestamp}>'

    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'price': self.price,
            'change_dollar': self.change_dollar,
            'change_percent': self.change_percent,
            'timestamp': self.timestamp.isoformat(),
            'location': self.location
        }


class ManualEntry(db.Model):
    """Manual entries for non-tradeable assets (401k, Cash, Property, Debt)"""
    __tablename__ = 'manual_entry'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))  # 401K, Cash, Property, Debt, Credit Card
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(50), default='Manual')

    def __repr__(self):
        return f'<ManualEntry {self.name} ${self.value}>'


class BusinessMetrics(db.Model):
    """Business tracking metrics"""
    __tablename__ = 'business_metrics'

    id = db.Column(db.Integer, primary_key=True)
    contractors_working = db.Column(db.Integer)
    monthly_revenue = db.Column(db.Float)
    monthly_burn = db.Column(db.Float, default=20000)
    date = db.Column(db.Date, default=datetime.utcnow)
    updated_by = db.Column(db.String(50))

    def __repr__(self):
        return f'<BusinessMetrics {self.date} - {self.contractors_working} contractors>'


class Expense(db.Model):
    """Monthly expense tracking"""
    __tablename__ = 'expense'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_business = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Expense {self.date} ${self.amount} - {self.category}>'


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
