from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from chronosmatch.engine import TradingEngine
from chronosmatch.protocol import Order


app = FastAPI(
    title="ChronosMatch API",
    description="Educational order-processing engine API",
    version="1.1.0",
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

engine = TradingEngine()


class OrderRequest(BaseModel):
    order_id: int = Field(gt=0)
    price_paise: int = Field(gt=0)
    quantity: int = Field(gt=0)
    side: str


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


@app.get("/orderbook")
def get_order_book(depth: int = 5):
    """Return the current limit order book."""
    if depth < 1 or depth > 100:
        raise HTTPException(
            status_code=422,
            detail="depth must be between 1 and 100",
        )

    return engine.get_order_book(depth=depth)


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
