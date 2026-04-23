import os

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.config import Config
from starlette.requests import Request

from api.deps import get_db
from api.models import User

router = APIRouter()

_config = Config(environ=os.environ)
_oauth = OAuth(_config)
_oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.environ.get("GOOGLE_CLIENT_ID", ""),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", ""),
    client_kwargs={"scope": "openid email profile"},
)

_ALLOWED_DOMAIN = "powned.tv"
_DEV_MODE = os.environ.get("DEV_MODE", "false").lower() == "true"
_DEV_EMAIL = os.environ.get("DEV_EMAIL", "dev@powned.tv")


def _is_allowed_email(email: str) -> bool:
    return email.endswith(f"@{_ALLOWED_DOMAIN}")


@router.get("/login")
async def login(request: Request):
    if _DEV_MODE:
        return RedirectResponse(url="/dev-login")
    redirect_uri = request.url_for("auth_callback")
    return await _oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback", name="auth_callback")
async def auth_callback(request: Request):
    token = await _oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo", {})
    email = user_info.get("email", "")

    if not _is_allowed_email(email):
        raise HTTPException(status_code=403, detail="Toegang beperkt tot @powned.tv medewerkers.")

    request.session["user_email"] = email
    return RedirectResponse(url="/")


@router.get("/dev-login")
async def dev_login(request: Request, db: Session = Depends(get_db)):
    """DEV_MODE only — bypass Google SSO for local development."""
    if not _DEV_MODE:
        raise HTTPException(status_code=404)
    request.session["user_email"] = _DEV_EMAIL
    user = db.query(User).filter(User.email == _DEV_EMAIL).first()
    if not user:
        user = User(email=_DEV_EMAIL)
        db.add(user)
        db.commit()
    return RedirectResponse(url="/")


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")
