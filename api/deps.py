from fastapi import Depends, Request
from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models import User


class NotAuthenticated(Exception):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    email = request.session.get("user_email")
    if not email:
        raise NotAuthenticated()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
