from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi import Request
from fastapi.responses import HTMLResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from api.models import FeedbackLog, Item, User
from api.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def feed(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    region: str | None = Query(default=None),
    min_score: int | None = Query(default=None),
):
    threshold = min_score if min_score is not None else user.score_threshold
    now = datetime.now(timezone.utc)

    query = (
        db.query(Item)
        .filter(
            Item.score >= threshold,
            or_(Item.expires_at > now, Item.expires_at.is_(None)),
        )
        .order_by(Item.score.desc())
    )

    if region:
        query = query.filter(Item.region == region)

    items = query.limit(150).all()

    hidden_ids = {
        fl.item_id
        for fl in db.query(FeedbackLog)
        .filter(FeedbackLog.user_id == user.id, FeedbackLog.action == "hide")
        .all()
    }
    favorite_ids = {
        fl.item_id
        for fl in db.query(FeedbackLog)
        .filter(FeedbackLog.user_id == user.id, FeedbackLog.action == "favorite")
        .all()
    }

    visible_items = [i for i in items if i.id not in hidden_ids]

    regions = [
        r for (r,) in db.query(Item.region).distinct().filter(Item.region.isnot(None)).all()
    ]

    return templates.TemplateResponse(
        "feed.html",
        {
            "request": request,
            "items": visible_items,
            "user": user,
            "regions": sorted(regions),
            "selected_region": region,
            "threshold": threshold,
            "favorite_ids": favorite_ids,
        },
    )
