from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from api.models import FeedbackLog, Item, User
from api.templates import templates

router = APIRouter()


@router.post("/items/{item_id}/feedback", response_class=HTMLResponse)
async def feedback(
    request: Request,
    item_id: int,
    action: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    db.query(FeedbackLog).filter(
        FeedbackLog.item_id == item_id,
        FeedbackLog.user_id == user.id,
        FeedbackLog.action == action,
    ).delete()

    log = FeedbackLog(
        item_id=item_id,
        user_id=user.id,
        action=action,
        created_at=datetime.now(timezone.utc),
    )
    db.add(log)

    item = db.get(Item, item_id)
    if item and action in ("favorite", "used"):
        item.expires_at = None

    db.commit()

    if action == "hide":
        return HTMLResponse("")

    is_favorite = action == "favorite"
    return templates.TemplateResponse(
        "partials/card.html",
        {
            "request": request,
            "item": item,
            "user": user,
            "is_favorite": is_favorite,
        },
    )
