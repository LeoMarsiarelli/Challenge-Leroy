from datetime import date, timedelta

from app.ai.demand_forecast import forecast_demand
from app.ai.route_optimizer import RouteNode, haversine_km, optimize_route


def _history(daily_units: list[int]) -> list[tuple[date, int]]:
    start = date.today() - timedelta(days=len(daily_units))
    return [(start + timedelta(days=i), u) for i, u in enumerate(daily_units)]


def test_forecast_demand_with_no_history_is_safe():
    result = forecast_demand([], current_stock=10, reorder_point=5, safety_stock_days=3)
    assert result.forecast == []
    assert result.suggested_replenishment == 0
    assert result.stockout_risk_days is None


def test_forecast_demand_projects_positive_trend():
    history = _history([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    result = forecast_demand(history, current_stock=20, reorder_point=15, safety_stock_days=3, horizon_days=5)

    assert len(result.forecast) == 5
    # tendencia de alta -> previsao deve crescer ao longo do horizonte
    assert result.forecast[-1][1] >= result.forecast[0][1]
    assert result.avg_daily_demand > 0


def test_forecast_suggests_replenishment_when_stock_is_low():
    history = _history([20] * 20)
    result = forecast_demand(history, current_stock=5, reorder_point=15, safety_stock_days=3, horizon_days=7)
    assert result.suggested_replenishment > 0


def test_forecast_suggests_no_replenishment_when_stock_is_abundant():
    history = _history([5] * 20)
    result = forecast_demand(history, current_stock=1000, reorder_point=15, safety_stock_days=3, horizon_days=7)
    assert result.suggested_replenishment == 0


def test_haversine_zero_distance_for_same_point():
    assert haversine_km(-23.55, -46.63, -23.55, -46.63) == 0


def test_haversine_known_distance_sp_rj():
    # Sao Paulo -> Rio de Janeiro, aproximadamente 360km em linha reta
    dist = haversine_km(-23.5505, -46.6333, -22.9068, -43.1729)
    assert 350 < dist < 370


def test_optimize_route_visits_all_destinations_once():
    origin = RouteNode(id=0, name="CD", city="Cajamar", latitude=-23.354, longitude=-46.877)
    destinations = [
        RouteNode(id=1, name="A", city="A", latitude=-23.656, longitude=-46.714),
        RouteNode(id=2, name="B", city="B", latitude=-22.905, longitude=-47.061),
        RouteNode(id=3, name="C", city="C", latitude=-23.501, longitude=-47.458),
        RouteNode(id=4, name="D", city="D", latitude=-23.454, longitude=-46.533),
    ]

    plan = optimize_route(origin, destinations)

    visited_ids = {stop.node.id for stop in plan.stops}
    assert visited_ids == {d.id for d in destinations}
    assert len(plan.stops) == len(destinations)


def test_optimize_route_never_worse_than_naive_order():
    origin = RouteNode(id=0, name="CD", city="Cajamar", latitude=-23.354, longitude=-46.877)
    destinations = [
        RouteNode(id=1, name="A", city="A", latitude=-23.656, longitude=-46.714),
        RouteNode(id=2, name="B", city="B", latitude=-22.905, longitude=-47.061),
        RouteNode(id=3, name="C", city="C", latitude=-23.501, longitude=-47.458),
        RouteNode(id=4, name="D", city="D", latitude=-23.454, longitude=-46.533),
        RouteNode(id=5, name="E", city="E", latitude=-23.532, longitude=-46.792),
    ]

    plan = optimize_route(origin, destinations)
    assert plan.total_distance_km <= plan.naive_distance_km


def test_optimize_route_empty_destinations():
    origin = RouteNode(id=0, name="CD", city="Cajamar", latitude=-23.354, longitude=-46.877)
    plan = optimize_route(origin, [])
    assert plan.stops == []
    assert plan.total_distance_km == 0.0
