"""
Self-contained demo server for the PowNed Feed UI.
Uses SQLite (no PostgreSQL needed) and pre-seeded fake data.
Run: .venv/bin/python demo_server.py
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

os.environ.setdefault("SECRET_KEY", "demo-secret-key-not-for-production")

from fastapi import BackgroundTasks, Depends, FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker
from starlette.middleware.sessions import SessionMiddleware

# ── Database ──────────────────────────────────────────────────────────────────

DB_PATH = "demo.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    type = Column(String(50))
    url = Column(String(500))
    region = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)
    items = relationship("Item", back_populates="source")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    url = Column(String(1000))
    url_hash = Column(String(64), unique=True, index=True)
    title = Column(String(500))
    summary = Column(Text, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    region = Column(String(100), nullable=True)
    published_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Float, nullable=True)
    score_reason = Column(Text, nullable=True)
    is_paywall = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    source = relationship("Source", back_populates="items")
    feedback = relationship("FeedbackLog", back_populates="item")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True, index=True)
    score_threshold = Column(Integer, default=40)
    feedback = relationship("FeedbackLog", back_populates="user")


class FeedbackLog(Base):
    __tablename__ = "feedback_log"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    item = relationship("Item", back_populates="feedback")
    user = relationship("User", back_populates="feedback")


Base.metadata.create_all(bind=engine)


# ── Seed data ─────────────────────────────────────────────────────────────────

FAKE_ITEMS = [
    {
        "source": "RTV Oost", "region": "Overijssel", "score": 87,
        "title": "Wethouder Almelo betrapt op parkeren op invalidenplek terwijl hij strenge handhaving belooft",
        "summary": "De wethouder van Almelo parkeerde zijn dienstauto herhaaldelijk op een invalidenparkeerplaats voor het gemeentehuis. Een omwonende filmde het en zette het op TikTok.",
        "reason": "Klassiek PowNed-goud: lokale gezagsdrager die zichzelf niet aan eigen regels houdt, filmpje gaat viraal.",
        "url": "https://www.rtvoost.nl", "is_paywall": False,
    },
    {
        "source": "NH Nieuws", "region": "Noord-Holland", "score": 82,
        "title": "Amsterdamse influencer slaat deurwaarder na ruzie over onbetaald Tesla-lease",
        "summary": "Een bekende Amsterdam-based lifestyle-influencer met 400k volgers op Instagram sloeg een deurwaarder die zijn Tesla-leaseauto kwam ophalen. Het incident werd gefilmd door omstanders.",
        "reason": "BN'er-drama met een ongepolijste rand — precies de chaos die PowNed's doelgroep vermakelijk vindt.",
        "url": "https://www.nhnieuws.nl", "is_paywall": False,
    },
    {
        "source": "GeenStijl", "region": "nationaal", "score": 79,
        "title": "Gemeente verbiedt barbecue in eigen tuin — bewoners steken massaal hun grill aan als protest",
        "summary": "De gemeente Utrecht verbood open vuur in tuinen vanwege droogte. Honderden bewoners reageerden met een barbecue-flashmob.",
        "reason": "Overheid die betuttelt + bewoners die massaal in opstand komen = PowNed-verhaal met virale potentie.",
        "url": "https://www.geenstijl.nl", "is_paywall": False,
    },
    {
        "source": "Omroep Brabant", "region": "Brabant", "score": 75,
        "title": "Eindhovense rapper Frenna zet ex-manager op straat na ruzie over royalties — advocaten ingeschakeld",
        "summary": "Rapper Frenna heeft zijn manager na jaren samenwerking ontslagen via een openbare Instagram-post. De manager reageerde met een uitgebreid tegenstatement.",
        "reason": "Bekende Nederlander, publiekelijk conflict, social media als slagveld — sterke PowNed-ingrediënten.",
        "url": "https://www.omroepbrabant.nl", "is_paywall": False,
    },
    {
        "source": "NOS Regio", "region": "nationaal", "score": 71,
        "title": "Tiener bouwt illegale casino in schuur — ouders ontdekken het via Snapchat-video",
        "summary": "Een 17-jarige jongen uit Zoetermeer had een volledig ingericht casino in de schuur van zijn ouders gebouwd, inclusief roulette en blackjack. Zijn ouders kwamen er pas achter toen een Snapchat-story viral ging.",
        "reason": "Absurd, herkenbaar voor jongeren en te gek voor woorden — scoort hoog bij de PowNed-doelgroep.",
        "url": "https://nos.nl/regio", "is_paywall": False,
    },
    {
        "source": "RTV Rijnmond", "region": "Zuid-Holland", "score": 68,
        "title": "Rotterdamse bijstandsfraudeur blijkt via TikTok duizenden volgers te hebben met luxeleven-content",
        "summary": "Een man die bijstandsuitkering ontving postte jarenlang video's van vakanties, restaurants en dure kleding. De gemeente Rotterdam ontdekte zijn TikTok-account bij een reguliere controle.",
        "reason": "Actueel, confronterend en herkenbaar — raakt aan gevoel van rechtvaardigheid bij jonge kijkers.",
        "url": "https://www.rtvrijmond.nl", "is_paywall": False,
    },
    {
        "source": "L1", "region": "Limburg", "score": 62,
        "title": "Burgemeester Maastricht verspreekt zich op live radio: 'We moeten inwoners gewoon negeren'",
        "summary": "De burgemeester van Maastricht maakte tijdens een live-uitzending een Freudian slip over het gemeentelijk inspraakproces. De radioclip circuleert nu breed op sociale media.",
        "reason": "Politicus die zich verspreekt op live radio — goede clip voor PowNed maar mist wat scherpte.",
        "url": "https://www.l1.nl", "is_paywall": False,
    },
    {
        "source": "Dagblad van het Noorden", "region": "Groningen", "score": 58,
        "title": "Groningse huisbaas verhoogt huur met 40% de dag nadat huurder klaagt bij huurcommissie",
        "summary": "Een verhuurder in Groningen stuurde een verhogingsbrief de dag nadat zijn huurder een klacht had ingediend. Huurder vermoedt vergelding.",
        "reason": "Relevante wooncrisis-insteek met een persoonlijk verhaal, maar mist de directe PowNed-punch.",
        "url": "https://www.dvhn.nl", "is_paywall": True,
    },
    {
        "source": "NOS Algemeen", "region": "nationaal", "score": 54,
        "title": "Kabinet presenteert plannen voor strengere handhaving onderhuur Airbnb",
        "summary": "Het kabinet wil gemeenten meer bevoegdheid geven om illegale Airbnb-verhuur aan te pakken. Amsterdam reageert positief.",
        "reason": "Relevant voor jongeren op woningmarkt, maar de beleidsmatige insteek mist de menselijke ingang die PowNed nodig heeft.",
        "url": "https://nos.nl", "is_paywall": False,
    },
    {
        "source": "Omroep Gelderland", "region": "Gelderland", "score": 49,
        "title": "Arnhemse horeca protesteert massaal tegen nieuwe geluidsnormen binnenstad",
        "summary": "Tientallen horecaondernemers in Arnhem lieten dinsdag hun terras onbemand achter als protest tegen nieuwe geluidsnormen die de gemeente wil invoeren.",
        "reason": "Lokaal protest met een beetje pit, maar te sectoraal voor een breed PowNed-publiek.",
        "url": "https://www.omroepgelderland.nl", "is_paywall": False,
    },
    {
        "source": "RTV Noord", "region": "Groningen", "score": 44,
        "title": "Groningse ondernemer opent eerste reparatiecafé voor elektrische fietsen",
        "summary": "In Groningen is het eerste gespecialiseerde reparatiecafé voor e-bikes geopend. Bezoekers kunnen hun fiets gratis laten nakijken.",
        "reason": "Leuk positief verhaal maar mist de confrontatie of het drama dat PowNed doorgaans zoekt.",
        "url": "https://www.rtvnoord.nl", "is_paywall": False,
    },
    {
        "source": "NOS Algemeen", "region": "nationaal", "score": 22,
        "title": "Minister van Infrastructuur opent nieuwe brug in Dordrecht",
        "summary": "De minister opende maandag de nieuwe Dordtse brug over de Oude Maas. Het project liep twee jaar vertraging op door materiaalgebrek.",
        "reason": "Standaard persmoment zonder PowNed-waarde — geen conflict, drama of menselijk verhaal.",
        "url": "https://nos.nl", "is_paywall": False,
    },
    {
        "source": "Omroep Brabant", "region": "Brabant", "score": 17,
        "title": "Gemeenteraad Tilburg bespreekt bestemmingsplan Spoorzone 2026",
        "summary": "De gemeenteraad van Tilburg vergaderde woensdag over de aanpassing van het bestemmingsplan voor de Spoorzone. Besluitvorming volgt in het najaar.",
        "reason": "Bestuurlijke procedure zonder urgent menselijk verhaal — ver buiten het PowNed-spectrum.",
        "url": "https://www.omroepbrabant.nl", "is_paywall": False,
    },
]


def seed_demo_data():
    db = SessionLocal()
    if db.query(Item).count() > 0:
        db.close()
        return

    user = User(email="redacteur@powned.tv", score_threshold=40)
    db.add(user)

    now = datetime.now(timezone.utc)
    sources_cache = {}

    for i, data in enumerate(FAKE_ITEMS):
        src_name = data["source"]
        if src_name not in sources_cache:
            source = Source(name=src_name, type="rss", url=f"https://demo/{src_name}", region=data["region"])
            db.add(source)
            db.flush()
            sources_cache[src_name] = source
        else:
            source = sources_cache[src_name]

        item = Item(
            url=data["url"],
            url_hash=f"demo-hash-{i}",
            title=data["title"],
            summary=data["summary"],
            source_id=source.id,
            region=data["region"],
            published_at=now - timedelta(hours=i * 2),
            scraped_at=now,
            score=data["score"],
            score_reason=data["reason"],
            is_paywall=data.get("is_paywall", False),
            expires_at=now + timedelta(days=30),
        )
        db.add(item)

    db.commit()
    db.close()
    print("  Demo data seeded.")


seed_demo_data()


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="PowNed Feed (demo)", docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key=os.environ["SECRET_KEY"])
app.mount("/static", StaticFiles(directory="web/static"), name="static")

templates = Jinja2Templates(directory="web/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    email = request.session.get("user_email", "redacteur@powned.tv")
    request.session["user_email"] = email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@app.get("/", response_class=HTMLResponse)
async def feed(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_user),
    region: Optional[str] = Query(default=None),
    min_score: Optional[int] = Query(default=None),
):
    from sqlalchemy import or_
    threshold = min_score if min_score is not None else user.score_threshold
    now = datetime.now(timezone.utc)

    query = (
        db.query(Item)
        .filter(Item.score >= threshold, or_(Item.expires_at > now, Item.expires_at.is_(None)))
        .order_by(Item.score.desc())
    )
    if region:
        query = query.filter(Item.region == region)
    items = query.limit(150).all()

    hidden_ids = {
        fl.item_id for fl in db.query(FeedbackLog)
        .filter(FeedbackLog.user_id == user.id, FeedbackLog.action == "hide").all()
    }
    favorite_ids = {
        fl.item_id for fl in db.query(FeedbackLog)
        .filter(FeedbackLog.user_id == user.id, FeedbackLog.action == "favorite").all()
    }

    visible_items = [i for i in items if i.id not in hidden_ids]
    regions = sorted({r for (r,) in db.query(Item.region).distinct().all() if r})

    return templates.TemplateResponse("feed.html", {
        "request": request,
        "items": visible_items,
        "user": user,
        "regions": regions,
        "selected_region": region,
        "threshold": threshold,
        "favorite_ids": favorite_ids,
    })


@app.post("/items/{item_id}/feedback", response_class=HTMLResponse)
async def feedback(
    request: Request,
    item_id: int,
    action: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_user),
):
    db.query(FeedbackLog).filter(
        FeedbackLog.item_id == item_id,
        FeedbackLog.user_id == user.id,
        FeedbackLog.action == action,
    ).delete()

    db.add(FeedbackLog(item_id=item_id, user_id=user.id, action=action))
    db.commit()

    if action == "hide":
        return HTMLResponse("")

    item = db.get(Item, item_id)
    return templates.TemplateResponse("partials/card.html", {
        "request": request,
        "item": item,
        "user": user,
        "is_favorite": action == "favorite",
    })


@app.post("/admin/run-pipeline")
async def trigger_pipeline(background_tasks: BackgroundTasks, _user: User = Depends(get_user)):
    def fake_run():
        import time; time.sleep(2)
        print("  [demo] Pipeline trigger received — in production this would scrape & score.")
    background_tasks.add_task(fake_run)
    return {"status": "started"}


if __name__ == "__main__":
    import uvicorn
    print("\n  PowNed Feed demo — http://localhost:8000\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
