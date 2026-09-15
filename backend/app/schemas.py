from datetime import date
from pydantic import BaseModel


class StoreOut(BaseModel):
    id: int
    name: str
    city: str
    state: str
    latitude: float
    longitude: float
    is_distribution_center: int

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    unit_cost: float
    safety_stock_days: int

    class Config:
        from_attributes = True


class InventoryOut(BaseModel):
    id: int
    store_id: int
    store_name: str
    product_id: int
    product_name: str
    quantity_on_hand: int
    reorder_point: int
    status: str


class ForecastPoint(BaseModel):
    day: str
    forecast_units: float


class ForecastOut(BaseModel):
    store_id: int
    store_name: str
    product_id: int
    product_name: str
    history: list
    forecast: list[ForecastPoint]
    avg_daily_demand: float
    current_stock: int
    suggested_replenishment: int
    stockout_risk_days: float | None = None


class RouteStop(BaseModel):
    order: int
    store_id: int
    store_name: str
    city: str
    distance_from_previous_km: float
    units_to_deliver: int


class RoutePlanOut(BaseModel):
    origin: str
    stops: list[RouteStop]
    total_distance_km: float
    naive_distance_km: float
    distance_saved_km: float
    distance_saved_pct: float
