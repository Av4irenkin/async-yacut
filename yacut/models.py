from datetime import datetime

from yacut import db


class URLMap(db.Model):
    __tablename__ = 'url_maps'

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'URLMap(original={self.original}, short={self.short})'
