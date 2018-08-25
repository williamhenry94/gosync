from app.database import sqla as db
from sqlalchemy.sql import func
from datetime import datetime


class FirebaseUser(db.Model):

    __tablename__ = 'firebase_users'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(191), nullable=False)

    email = db.Column(db.String(191), nullable=False)

    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now())
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, uid, email, deleted_at):

        self.uid = uid
        self.email = email
        self.deleted_at = deleted_at
