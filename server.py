# server.py — adaptor FastAPI care folosește backend-ul existent (fără modificări)
# Endpoints pentru frontend:
#   POST   /api/auth/register        {email, password}
#   POST   /api/auth/login           {email, password} -> {token}
#   GET    /api/account              (Bearer token)
#   POST   /api/hotels/search        {city, checkIn, checkOut, budget?, adults, minRating?}
#   GET    /api/favorites            (Bearer)
#   POST   /api/favorites            (Bearer) body: {hotelId, payload}
#   DELETE /api/favorites/{id}       (Bearer)
#   GET    /api/history              (Bearer)
#   POST   /api/history              (Bearer) body: {city, checkIn, checkOut, budget?, adults, minRating?}

from __future__ import annotations

import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from pydantic import BaseModel, EmailStr, Field

# ---------- .env înainte de importul backend-ului ----------
ROOT = Path(__file__).parent.resolve()
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=ROOT / ".env", override=False)
except Exception:
    pass

# Asigură-te că folderul curent e în sys.path (pentru import baza.py)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---------- Import backend existent ----------
try:
    import importlib
    baza = importlib.import_module("baza")
except Exception:
    baza = None

# transport: întâi transport.py, apoi fallback new_transport.py
try:
    from transport import cel_mai_apropiat_transport  # type: ignore
except Exception:
    try:
        from new_transport import cel_mai_apropiat_transport  # type: ignore
    except Exception:
        cel_mai_apropiat_transport = None  # type: ignore

# conversie valută
try:
    from schimb_euro import convert_to_euro
except Exception:
    convert_to_euro = None  # type: ignore

# ---------- Config ----------
APP_NAME = "Proiect_echipa5 API"
DATA_DIR = Path(os.getenv("APP_DATA_DIR", "./app_data"))
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"
FAVORITES_FILE = DATA_DIR / "favorites.json"
HISTORY_FILE = DATA_DIR / "history.json"

# ---------- Mini storage JSON ----------
def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _write_json(path: Path, data):
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)

# ---------- Modele ----------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class AccountOut(BaseModel):
    email: EmailStr
    createdAt: Optional[str] = None

class SearchIn(BaseModel):
    city: str
    checkIn: str
    checkOut: str
    budget: Optional[float] = None
    adults: int = 1
    minRating: Optional[float] = None

class Hotel(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    priceEUR: Optional[float] = None
    currency: Optional[str] = None
    rating: Optional[float] = None
    distanceToTransitMin: Optional[int] = None
    transitName: Optional[str] = None
    imageUrl: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None

class FavoriteIn(BaseModel):
    hotelId: str
    payload: Dict[str, Any]

# ---------- Auth ----------
security = HTTPBearer(auto_error=True)

def _load_users():
    return _read_json(USERS_FILE, {})

def _save_users(d):
    _write_json(USERS_FILE, d)

def _load_sessions():
    return _read_json(SESSIONS_FILE, {})

def _save_sessions(d):
    _write_json(SESSIONS_FILE, d)

def _get_email_from_token(token: str) -> Optional[str]:
    return _load_sessions().get(token)

def _create_session(email: str) -> str:
    sessions = _load_sessions()
    token = uuid.uuid4().hex
    sessions[token] = email
    _save_sessions(sessions)
    return token

def _require_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = creds.credentials
    email = _get_email_from_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return email

# ---------- Integrare backend existent ----------
def _fetch_hotels_from_backend(city: str, check_in: str, check_out: str,
                               budget: Optional[float], adults: int,
                               min_rating: Optional[float]) -> List[Hotel]:
    """Folosește direct baza.py + Amadeus + schimb_euro + transport fără a modifica backend-ul."""
    if baza is None:
        raise HTTPException(status_code=500, detail="Nu pot importa baza.py din backend.")

    # 1) Cod IATA pentru oraș
    city_code = baza.obtine_city_code_hotel(city)  # type: ignore[attr-defined]
    if not city_code:
        raise HTTPException(status_code=404, detail="Orașul nu a fost găsit sau nu are hoteluri.")

    # 2) ID-uri de hotel pentru oraș
    hotel_ids = baza.obtine_hoteluri_oras(city_code)  # type: ignore[attr-defined]
    if not hotel_ids:
        raise HTTPException(status_code=404, detail="Nu am găsit hoteluri pentru orașul dat.")

    amadeus = getattr(baza, "amadeus", None)
    if amadeus is None:
        raise HTTPException(status_code=500, detail="Clientul Amadeus nu e inițializat în baza.py")

    results: List[Hotel] = []
    limit = 10

    for hid in hotel_ids:
        if len(results) >= limit:
            break
        try:
            resp = amadeus.shopping.hotel_offers_search.get(
                hotelIds=hid,
                checkInDate=check_in,
                checkOutDate=check_out,
                adults=max(1, int(adults)),
            )
        except Exception:
            continue

        data = getattr(resp, "data", None)
        if not data:
            continue

        for oferta in data:
            hotel = oferta.get("hotel", {})
            name = hotel.get("name", f"Hotel {hid}")
            raw_rating = hotel.get("rating")
            # NORMALIZARE RATING la 1 zecimală
            try:
                rating = round(float(raw_rating), 1) if raw_rating is not None else None
            except Exception:
                rating = None

            geo = hotel.get("geoCode") or {}
            lat, lon = geo.get("latitude"), geo.get("longitude")

            price_eur: Optional[float] = None
            currency = None
            try:
                if oferta.get("offers"):
                    price_obj = oferta["offers"][0]["price"]
                    currency = price_obj.get("currency")
                    total = float(price_obj.get("total"))
                    if convert_to_euro and currency:
                        price_eur = round(float(convert_to_euro(total, currency)), 2)
                    else:
                        price_eur = total if currency == "EUR" else None
            except Exception:
                pass

            # filtrare pe buget
            if budget is not None and price_eur is not None and price_eur > budget:
                continue

            # filtrare pe rating minim
            if min_rating is not None:
                if rating is None:
                    continue
                try:
                    if float(rating) < float(min_rating):
                        continue
                except Exception:
                    continue

            # transport public (opțional)
            dist_minutes = None
            transit_name = None
            if cel_mai_apropiat_transport and (lat is not None and lon is not None):
                try:
                    info = cel_mai_apropiat_transport(lat, lon)
                    if isinstance(info, dict):
                        transit_name = info.get("station_name")
                        dur = str(info.get("duration") or "")
                        # extrage primul număr de minute din text
                        for token in dur.split():
                            if token.isdigit():
                                dist_minutes = int(token)
                                break
                except Exception:
                    pass

            results.append(Hotel(
                id=str(hid),
                name=str(name),
                address=(hotel.get("address", {}).get("lines", [None])[0]
                         if isinstance(hotel.get("address"), dict) else None),
                priceEUR=price_eur,
                currency=currency,
                rating=rating,
                distanceToTransitMin=dist_minutes,
                transitName=transit_name,
                imageUrl=None,
                raw=oferta,
            ))

            if len(results) >= limit:
                break

    return results

# ---------- FastAPI app ----------
app = FastAPI(title=APP_NAME)

# CORS — permisiv pentru dev (acceptă inclusiv 127.0.0.1:5500)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- API routes ----------
@app.post("/api/auth/register")
def register(payload: RegisterIn):
    users = _load_users()
    if payload.email in users:
        raise HTTPException(status_code=400, detail="Email deja folosit")
    users[payload.email] = {
        "password": payload.password,  # pentru producție folosește hashing
        "createdAt": datetime.utcnow().isoformat() + "Z",
    }
    _save_users(users)
    return {"ok": True}

@app.post("/api/auth/login")
def login(payload: LoginIn):
    users = _load_users()
    user = users.get(payload.email)
    if not user or user.get("password") != payload.password:
        raise HTTPException(status_code=401, detail="Credențiale invalide")
    token = _create_session(payload.email)
    return {"token": token}

@app.get("/api/account", response_model=AccountOut)
def account(email: str = Depends(_require_user)):
    users = _load_users()
    u = users.get(email, {})
    return AccountOut(email=email, createdAt=u.get("createdAt"))

@app.post("/api/hotels/search", response_model=Dict[str, List[Hotel]])
def hotels_search(q: SearchIn):
    hotels = _fetch_hotels_from_backend(
        q.city, q.checkIn, q.checkOut,
        q.budget, q.adults, q.minRating
    )
    return {"results": hotels}

def _load_map_file(path: Path) -> Dict[str, Dict[str, Any]]:
    return _read_json(path, {})

def _save_map_file(path: Path, data: Dict[str, Dict[str, Any]]):
    _write_json(path, data)

@app.get("/api/favorites")
def get_favorites(email: str = Depends(_require_user)):
    data = _load_map_file(FAVORITES_FILE)
    favs = data.get(email, {})
    out = []
    for hid, payload in favs.items():
        try:
            h = Hotel(id=str(hid), **payload)
        except Exception:
            payload = {"id": hid, **(payload if isinstance(payload, dict) else {})}
            h = Hotel(**payload)  # type: ignore
        out.append(h)
    return out

@app.post("/api/favorites")
def add_favorite(body: FavoriteIn, email: str = Depends(_require_user)):
    data = _load_map_file(FAVORITES_FILE)
    user_map = data.get(email, {})
    user_map[body.hotelId] = body.payload
    data[email] = user_map
    _save_map_file(FAVORITES_FILE, data)
    return {"ok": True}

@app.delete("/api/favorites/{hotel_id}")
def delete_favorite(hotel_id: str, email: str = Depends(_require_user)):
    data = _load_map_file(FAVORITES_FILE)
    user_map = data.get(email, {})
    if hotel_id in user_map:
        del user_map[hotel_id]
        data[email] = user_map
        _save_map_file(FAVORITES_FILE, data)
    return {"ok": True}

@app.get("/api/history")
def get_history(email: str = Depends(_require_user)):
    data = _load_map_file(HISTORY_FILE)
    return list(data.get(email, {}).values())

@app.post("/api/history")
def add_history(entry: SearchIn, email: str = Depends(_require_user)):
    data = _load_map_file(HISTORY_FILE)
    user_map = data.get(email, {})
    key = uuid.uuid4().hex
    user_map[key] = entry.dict()
    data[email] = user_map
    _save_map_file(HISTORY_FILE, data)
    return {"ok": True}

@app.get("/api/health")
def health():
    return {"ok": True, "name": APP_NAME, "time": datetime.utcnow().isoformat() + "Z"}

# ---------- STATIC (Varianta A) ----------
# Servește index.html la "/" și restul resurselor sub /static
static_dir = ROOT / "static"

@app.get("/")
def root_page():
    if static_dir.exists():
        return FileResponse(static_dir / "index.html")
    return RedirectResponse(url="/docs")

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

# ---------- Run (dev) ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 5000)), reload=True)
