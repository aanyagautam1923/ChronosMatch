from pathlib import Path
import os
import secrets

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

from chronosmatch.engine import TradingEngine
from chronosmatch.protocol import Order
app = FastAPI(
    title="ChronosMatch API",
    description="Educational order-processing engine API",
    version="1.2.0",
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
engine = TradingEngine()


class OrderRequest(BaseModel):
    order_id: int = Field(gt=0)
    price_paise: int = Field(gt=0)
    quantity: int = Field(gt=0)
    side: str


session_secret = os.getenv("CHRONOSMATCH_SESSION_SECRET")
if not session_secret:
    session_secret = secrets.token_urlsafe(48)
    import warnings
    warnings.warn(
        "CHRONOSMATCH_SESSION_SECRET is not set. Sessions will reset on restart.",
        RuntimeWarning,
    )

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/orders")
def create_order(request: OrderRequest):
    side = request.side.upper()

    if side not in ("B", "S"):
        raise HTTPException(
            status_code=422,
            detail="side must be B (buy) or S (sell)",
        )

    try:
        order = Order(
            request.order_id,
            request.price_paise,
            request.quantity,
            side,
        )
        return engine.process_order(order)
    except (ValueError, TypeError, OverflowError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/orders")
def list_orders():
    return [
        {
            "order_id": order.order_id,
            "side": order.side.upper(),
            "price_paise": order.price_paise,
            "quantity": order.quantity,
            "status": "accepted",
        }
        for order in reversed(engine.orders)
    ]


@app.get("/stats")
def stats():
    result = engine.get_stats()
    result.update(engine.get_performance_stats())
    result["components"] = {
        "protocol": "online",
        "ring_buffer": "available",
        "matching_engine": "online",
        "firehose": "not_started",
    }
    return result
