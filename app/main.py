from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from chronosmatch.engine import TradingEngine
from chronosmatch.protocol import Order

app = FastAPI(
    title="ChronosMatch API",
    description="Educational order-processing engine API",
    version="1.0.0",
)

engine = TradingEngine()


class OrderRequest(BaseModel):
    order_id: int = Field(gt=0)
    price_paise: int = Field(gt=0)
    quantity: int = Field(gt=0)
    side: str


@app.get("/")
def home():
    return {
        "project": "ChronosMatch",
        "status": "online",
        "message": "Educational trading engine API",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/orders")
def create_order(request: OrderRequest):
    side = request.side.upper()

    if side not in ("B", "S"):
        raise HTTPException(
            status_code=422,
            detail="Side must be B (buy) or S (sell)",
        )

    order = Order(
        request.order_id,
        request.price_paise,
        request.quantity,
        side,
    )

    try:
        return engine.process_order(order)
    except (ValueError, TypeError, OverflowError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/stats")
def get_stats():
    return engine.get_stats()
