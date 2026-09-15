"""AI Logistics Extension - modulo de previsao de demanda.

Usa suavizacao exponencial dupla (Holt) sobre o historico de vendas diarias
de um produto em uma loja para projetar a demanda dos proximos dias e
sugerir a quantidade de reposicao considerando o estoque atual e o
estoque de seguranca do produto.
"""
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class ForecastResult:
    history: list[tuple[date, int]]
    forecast: list[tuple[date, float]]
    avg_daily_demand: float
    suggested_replenishment: int
    stockout_risk_days: float | None


def _holt_double_exponential_smoothing(
    series: list[float], alpha: float = 0.4, beta: float = 0.2
) -> tuple[float, float]:
    """Retorna (nivel, tendencia) suavizados ao final da serie."""
    if not series:
        return 0.0, 0.0
    level = series[0]
    trend = series[1] - series[0] if len(series) > 1 else 0.0

    for value in series[1:]:
        prev_level = level
        level = alpha * value + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend

    return level, trend


def forecast_demand(
    sales_history: list[tuple[date, int]],
    current_stock: int,
    reorder_point: int,
    safety_stock_days: int,
    horizon_days: int = 7,
) -> ForecastResult:
    """Projeta a demanda diaria para os proximos `horizon_days` dias.

    `sales_history` deve vir ordenado do mais antigo para o mais recente.
    """
    if not sales_history:
        return ForecastResult(history=[], forecast=[], avg_daily_demand=0.0,
                               suggested_replenishment=0, stockout_risk_days=None)

    units = [float(u) for _, u in sales_history]
    level, trend = _holt_double_exponential_smoothing(units)

    last_date = sales_history[-1][0]
    forecast_points: list[tuple[date, float]] = []
    for step in range(1, horizon_days + 1):
        projected = max(0.0, level + trend * step)
        forecast_points.append((last_date + timedelta(days=step), round(projected, 1)))

    # media movel das ultimas 2 semanas como leitura robusta de demanda diaria
    recent_window = units[-14:] if len(units) >= 14 else units
    avg_daily_demand = sum(recent_window) / len(recent_window)

    projected_horizon_demand = sum(p for _, p in forecast_points)
    safety_stock_units = avg_daily_demand * safety_stock_days

    # repor o suficiente para cobrir a demanda projetada + estoque de seguranca,
    # descontando o que ja esta disponivel na loja
    needed = projected_horizon_demand + safety_stock_units - current_stock
    suggested_replenishment = max(0, round(needed))

    stockout_risk_days = None
    if avg_daily_demand > 0:
        stockout_risk_days = round(current_stock / avg_daily_demand, 1)

    return ForecastResult(
        history=sales_history,
        forecast=forecast_points,
        avg_daily_demand=round(avg_daily_demand, 2),
        suggested_replenishment=suggested_replenishment,
        stockout_risk_days=stockout_risk_days,
    )
