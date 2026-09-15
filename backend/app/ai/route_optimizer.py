"""AI Logistics Extension - modulo de roteirizacao de entregas.

Recebe o Centro de Distribuicao (origem) e um conjunto de lojas que
precisam de reposicao, e calcula uma rota otimizada usando a heuristica
do vizinho mais proximo seguida de refinamento 2-opt, minimizando a
distancia total percorrida (formula de Haversine sobre lat/lon).
"""
import math
from dataclasses import dataclass


@dataclass
class RouteNode:
    id: int
    name: str
    city: str
    latitude: float
    longitude: float
    units_to_deliver: int = 0


@dataclass
class RouteStopResult:
    order: int
    node: RouteNode
    distance_from_previous_km: float


@dataclass
class RoutePlanResult:
    stops: list[RouteStopResult]
    total_distance_km: float
    naive_distance_km: float


EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _route_distance(origin: RouteNode, ordered_stops: list[RouteNode]) -> float:
    total = 0.0
    previous = origin
    for stop in ordered_stops:
        total += haversine_km(previous.latitude, previous.longitude, stop.latitude, stop.longitude)
        previous = stop
    return total


def _nearest_neighbor_order(origin: RouteNode, destinations: list[RouteNode]) -> list[RouteNode]:
    remaining = list(destinations)
    ordered: list[RouteNode] = []
    current = origin

    while remaining:
        nearest = min(remaining, key=lambda d: haversine_km(current.latitude, current.longitude, d.latitude, d.longitude))
        ordered.append(nearest)
        remaining.remove(nearest)
        current = nearest

    return ordered


def _two_opt(origin: RouteNode, ordered_stops: list[RouteNode]) -> list[RouteNode]:
    """Refinamento 2-opt classico: troca pares de arestas enquanto reduzir a distancia total."""
    best = ordered_stops
    best_distance = _route_distance(origin, best)
    improved = True

    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                candidate = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                candidate_distance = _route_distance(origin, candidate)
                if candidate_distance + 1e-9 < best_distance:
                    best, best_distance = candidate, candidate_distance
                    improved = True
    return best


def optimize_route(origin: RouteNode, destinations: list[RouteNode]) -> RoutePlanResult:
    if not destinations:
        return RoutePlanResult(stops=[], total_distance_km=0.0, naive_distance_km=0.0)

    naive_distance = _route_distance(origin, destinations)

    nn_order = _nearest_neighbor_order(origin, destinations)
    optimized_order = _two_opt(origin, nn_order)

    stops: list[RouteStopResult] = []
    previous = origin
    for idx, node in enumerate(optimized_order, start=1):
        dist = haversine_km(previous.latitude, previous.longitude, node.latitude, node.longitude)
        stops.append(RouteStopResult(order=idx, node=node, distance_from_previous_km=round(dist, 2)))
        previous = node

    total_distance = _route_distance(origin, optimized_order)

    return RoutePlanResult(
        stops=stops,
        total_distance_km=round(total_distance, 2),
        naive_distance_km=round(naive_distance, 2),
    )
