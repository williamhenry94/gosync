from app.database import sqla
from app.models.Translink import Translink
from datetime import datetime


def store(data):

    translink_account = Translink(
        gocard_number=data['gocard_number'],
        password=data['password'],
        deleted_at=None
    )
    sqla.session.add(translink_account)
    sqla.session.commit()
    sqla.session.refresh(translink_account)

    return translink_account


def edit(id, data):

    translink_account = Translink.query.filter_by(
        id=id, deleted_at=None).first()

    if translink_account:
        translink_account.gocard_number = data['gocard_number']
        translink_account.password = data['password']
        sqla.session.commit()
        return True
    else:
        return False


def delete(id):

    translink_account = Translink.query.filter_by(
        id=id, deleted_at=None).first()

    if translink_account:
        translink_account.deleted_at = datetime.utcnow()
        sqla.session.commit()
        return True
    else:
        return False


def get_account(id):

    translink_account = Translink.query.filter_by(
        deleted_at=None, id=id).first()
    if translink_account:
        translink_account = translink_account.__dict__
        translink_account.pop('_sa_instance_state', None)

        return translink_account

    return None
