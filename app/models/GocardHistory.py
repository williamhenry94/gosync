from app.database import sqla as db
from sqlalchemy.sql import func
from datetime import datetime


class GocardHistory(db.Model):

    __tablename__ = 'gocard_histories'

    id = db.Column(db.Integer, primary_key=True)
    from_station = db.Column(db.String(255), nullable=False)
    to_station = db.Column(db.String(255), nullable=True)

    fare = db.Column(db.Float, nullable=True)
    credit = db.Column(db.Float, nullable=True)
    balance = db.Column(db.Float, nullable=True)

    from_datetime = db.Column(db.DateTime, nullable=False)
    to_datetime = db.Column(db.DateTime, nullable=True)
    hashed_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, from_station, to_station, fare, credit, balance, from_datetime, to_datetime, hashed_id, deleted_at):

        self.from_station = from_station
        self.to_station = to_station
        self.fare = fare
        self.credit = credit
        self.balance = balance
        self.from_datetime = from_datetime
        self.to_datetime = to_datetime
        self.hashed_id = hashed_id
        self.deleted_at = deleted_at
