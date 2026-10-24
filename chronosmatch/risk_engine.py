"""Configurable order risk validation for the ChronosMatch simulation."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RiskLimits:
    max_quantity: int = 10_000
    min_price_paise: int = 1
    max_price_paise: int = 10_000_000
    large_order_quantity: int = 5_000


@dataclass(frozen=True)
class RiskResult:
    accepted: bool
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]


class OrderRiskEngine:
    """Validate order fields without modifying the matching engine."""

    def __init__(self, limits: RiskLimits | None = None):
        self.limits = limits or RiskLimits()

        if self.limits.max_quantity <= 0:
            raise ValueError("max_quantity must be positive.")
        if self.limits.min_price_paise <= 0:
            raise ValueError("min_price_paise must be positive.")
        if self.limits.max_price_paise < self.limits.min_price_paise:
            raise ValueError("Maximum price must be >= minimum price.")
        if self.limits.large_order_quantity < 1:
            raise ValueError("large_order_quantity must be positive.")

    def validate(self, order) -> RiskResult:
        reasons = []
        warnings = []

        side = getattr(order, "side", None)
        quantity = getattr(order, "quantity", None)
        price = getattr(order, "price_paise", None)

        if not isinstance(side, str) or side.upper() not in {"B", "S"}:
            reasons.append("Side must be 'B' (buy) or 'S' (sell).")

        if type(quantity) is not int or quantity <= 0:
            reasons.append("Quantity must be a positive integer.")
        elif quantity > self.limits.max_quantity:
            reasons.append("Quantity exceeds the configured maximum.")
        elif quantity >= self.limits.large_order_quantity:
            warnings.append("Large order: additional review recommended.")

        if type(price) is not int or price <= 0:
            reasons.append("Price must be a positive integer in paise.")
        elif not (
            self.limits.min_price_paise
            <= price
            <= self.limits.max_price_paise
        ):
            reasons.append("Price is outside the configured allowed range.")

        return RiskResult(
            accepted=not reasons,
            reasons=tuple(reasons),
            warnings=tuple(warnings),
        )
