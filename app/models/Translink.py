from app.database import sqla as db
from sqlalchemy.sql import func
from datetime import datetime


class Translink(db.Model):

    __tablename__ = 'translink'

    id = db.Column(db.Integer, primary_key=True)
    gocard_number = db.Column(db.String(16), nullable=False)

    password = db.Column(db.String(191), nullable=False)

    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, gocard_number, password, deleted_at):

        self.gocard_number = gocard_number
        self.password = password
        self.deleted_at = deleted_at
