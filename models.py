from flask_sqlalchemy import SQLAlchemy
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
    ticker = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    change_dollar = db.Column(db.Float)
    change_percent = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
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
