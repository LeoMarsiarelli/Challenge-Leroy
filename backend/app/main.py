import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import models, schemas
from .ai.demand_forecast import forecast_demand
from .ai.route_optimizer import RouteNode, optimize_route
from .database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Leroy Merlin Smart Hub — AI Logistics Extension",
    description="API do Smart Hub com a camada de IA para previsao de demanda e roteirizacao de entregas.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stores", response_model=list[schemas.StoreOut])
def list_stores():
    db = SessionLocal()
    try:
        return db.query(models.Store).order_by(models.Store.is_distribution_center.desc(), models.Store.name).all()
    finally:
        db.close()


@app.get("/api/products", response_model=list[schemas.ProductOut])
def list_products():
    db = SessionLocal()
    try:
        return db.query(models.Product).order_by(models.Product.name).all()
    finally:
        db.close()


@app.get("/api/inventory", response_model=list[schemas.InventoryOut])
def list_inventory(store_id: int | None = None):
    db = SessionLocal()
    try:
        query = db.query(models.Inventory)
        if store_id is not None:
            query = query.filter(models.Inventory.store_id == store_id)

        result = []
        for inv in query.all():
            status = "critico" if inv.quantity_on_hand <= inv.reorder_point else "ok"
            result.append(schemas.InventoryOut(
                id=inv.id,
                store_id=inv.store_id,
                store_name=inv.store.name,
                product_id=inv.product_id,
                product_name=inv.product.name,
                quantity_on_hand=inv.quantity_on_hand,
                reorder_point=inv.reorder_point,
                status=status,
            ))
        return result
    finally:
        db.close()


@app.get("/api/forecast/{store_id}/{product_id}", response_model=schemas.ForecastOut)
def get_forecast(store_id: int, product_id: int, horizon_days: int = Query(7, ge=1, le=30)):
    db = SessionLocal()
    try:
        inv = (
            db.query(models.Inventory)
            .filter(models.Inventory.store_id == store_id, models.Inventory.product_id == product_id)
            .first()
        )
        if inv is None:
            raise HTTPException(status_code=404, detail="Combinação loja/produto não encontrada")

        history_rows = (
            db.query(models.SalesHistory)
            .filter(models.SalesHistory.inventory_id == inv.id)
            .order_by(models.SalesHistory.sale_date)
            .all()
        )
        history = [(row.sale_date, row.units_sold) for row in history_rows]

        result = forecast_demand(
            sales_history=history,
            current_stock=inv.quantity_on_hand,
            reorder_point=inv.reorder_point,
            safety_stock_days=inv.product.safety_stock_days,
            horizon_days=horizon_days,
        )

        return schemas.ForecastOut(
            store_id=inv.store_id,
            store_name=inv.store.name,
            product_id=inv.product_id,
            product_name=inv.product.name,
            history=[{"day": d.isoformat(), "units_sold": u} for d, u in result.history],
            forecast=[schemas.ForecastPoint(day=d.isoformat(), forecast_units=v) for d, v in result.forecast],
            avg_daily_demand=result.avg_daily_demand,
            current_stock=inv.quantity_on_hand,
            suggested_replenishment=result.suggested_replenishment,
            stockout_risk_days=result.stockout_risk_days,
        )
    finally:
        db.close()


@app.get("/api/logistics/route-plan", response_model=schemas.RoutePlanOut)
def get_route_plan():
    """Combina a previsao de demanda com a roteirizacao: identifica lojas com
    estoque critico, calcula a reposicao sugerida por produto e monta a rota
    otimizada de entrega a partir do Centro de Distribuicao."""
    db = SessionLocal()
    try:
        cd = db.query(models.Store).filter(models.Store.is_distribution_center == 1).first()
        if cd is None:
            raise HTTPException(status_code=500, detail="Centro de Distribuição não configurado")

        stores = db.query(models.Store).filter(models.Store.is_distribution_center == 0).all()

        stops_by_store: dict[int, int] = {}
        for store in stores:
            total_units = 0
            for inv in store.inventories:
                if inv.quantity_on_hand > inv.reorder_point:
                    continue
                history_rows = (
                    db.query(models.SalesHistory)
                    .filter(models.SalesHistory.inventory_id == inv.id)
                    .order_by(models.SalesHistory.sale_date)
                    .all()
                )
                history = [(row.sale_date, row.units_sold) for row in history_rows]
                result = forecast_demand(
                    sales_history=history,
                    current_stock=inv.quantity_on_hand,
                    reorder_point=inv.reorder_point,
                    safety_stock_days=inv.product.safety_stock_days,
                )
                total_units += result.suggested_replenishment

            if total_units > 0:
                stops_by_store[store.id] = total_units

        destinations = [
            RouteNode(
                id=store.id,
                name=store.name,
                city=store.city,
                latitude=store.latitude,
                longitude=store.longitude,
                units_to_deliver=stops_by_store[store.id],
            )
            for store in stores
            if store.id in stops_by_store
        ]

        origin = RouteNode(id=cd.id, name=cd.name, city=cd.city, latitude=cd.latitude, longitude=cd.longitude)
        plan = optimize_route(origin, destinations)

        saved = plan.naive_distance_km - plan.total_distance_km
        saved_pct = (saved / plan.naive_distance_km * 100) if plan.naive_distance_km > 0 else 0.0

        return schemas.RoutePlanOut(
            origin=cd.name,
            stops=[
                schemas.RouteStop(
                    order=s.order,
                    store_id=s.node.id,
                    store_name=s.node.name,
                    city=s.node.city,
                    distance_from_previous_km=s.distance_from_previous_km,
                    units_to_deliver=s.node.units_to_deliver,
                )
                for s in plan.stops
            ],
            total_distance_km=plan.total_distance_km,
            naive_distance_km=plan.naive_distance_km,
            distance_saved_km=round(saved, 2),
            distance_saved_pct=round(saved_pct, 1),
        )
    finally:
        db.close()


@app.get("/api/dashboard/summary")
def dashboard_summary():
    db = SessionLocal()
    try:
        total_stores = db.query(models.Store).filter(models.Store.is_distribution_center == 0).count()
        total_products = db.query(models.Product).count()
        critical_items = (
            db.query(models.Inventory)
            .filter(models.Inventory.quantity_on_hand <= models.Inventory.reorder_point)
            .count()
        )
        total_items = db.query(models.Inventory).count()

        return {
            "total_stores": total_stores,
            "total_products": total_products,
            "critical_items": critical_items,
            "total_inventory_records": total_items,
            "critical_pct": round((critical_items / total_items * 100) if total_items else 0, 1),
        }
    finally:
        db.close()


_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
