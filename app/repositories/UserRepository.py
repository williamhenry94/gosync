from app.models.User import FirebaseUser
from app.database import sqla


def get_or_create_user(data):

    user = FirebaseUser.query.filter_by(
        uid=data['uid'], email=data['email'], deleted_at=None).first()

    if not user:
        user = FirebaseUser(
            uid=data['uid'], email=data['email'], deleted_at=None)

        sqla.session.add(user)
        sqla.session.commit()
        sqla.session.refresh(user)

        return user
    else:
        return user
