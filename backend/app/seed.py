"""Popula o banco com uma rede fictícia de lojas Leroy Merlin (regiao Sudeste),
um Centro de Distribuicao e 30 dias de historico de vendas por produto/loja,
usado pela AI Logistics Extension para previsao de demanda e roteirizacao.
"""
import random
from datetime import date, timedelta

from .database import Base, engine, SessionLocal
from .models import Store, Product, Inventory, SalesHistory

random.seed(42)

STORES = [
    # name, city, state, lat, lon, is_cd
    ("Centro de Distribuição Cajamar", "Cajamar", "SP", -23.3540, -46.8770, 1),
    ("Loja Santo Amaro", "São Paulo", "SP", -23.6560, -46.7140, 0),
    ("Loja Raposo Tavares", "São Paulo", "SP", -23.5940, -46.7750, 0),
    ("Loja Anália Franco", "São Paulo", "SP", -23.5580, -46.5660, 0),
    ("Loja ABC Santo André", "Santo André", "SP", -23.6640, -46.5380, 0),
    ("Loja Campinas", "Campinas", "SP", -22.9050, -47.0610, 0),
    ("Loja Sorocaba", "Sorocaba", "SP", -23.5010, -47.4580, 0),
    ("Loja Osasco", "Osasco", "SP", -23.5320, -46.7920, 0),
    ("Loja Guarulhos", "Guarulhos", "SP", -23.4540, -46.5330, 0),
]

PRODUCTS = [
    # sku, name, category, unit_cost, safety_stock_days, base_daily_demand
    ("CIM-CPII-50", "Cimento CP-II 50kg", "Construção", 34.90, 2, 18),
    ("FUR-750W", "Furadeira de Impacto 750W", "Ferramentas", 289.90, 4, 3),
    ("TIN-ACR-18L", "Tinta Acrílica Branca 18L", "Tintas", 249.90, 3, 5),
    ("ARG-AC2-20", "Argamassa ACII 20kg", "Construção", 22.50, 2, 14),
    ("LAMP-LED-9W", "Lâmpada LED 9W", "Elétrica", 12.90, 3, 22),
    ("TUB-PVC-100", "Tubo PVC Esgoto 100mm 6m", "Hidráulica", 78.90, 4, 6),
    ("GRAM-SINT-M2", "Grama Sintética (m²)", "Jardim", 39.90, 5, 4),
    ("PARAF-KIT-100", "Kit Parafusos 100pçs", "Ferramentas", 15.90, 3, 12),
]

# fator de porte de cada loja (loja maior vende mais, CD nao vende ao consumidor)
STORE_FACTOR = {
    "Centro de Distribuição Cajamar": 0.0,
    "Loja Santo Amaro": 1.4,
    "Loja Raposo Tavares": 1.2,
    "Loja Anália Franco": 1.1,
    "Loja ABC Santo André": 0.9,
    "Loja Campinas": 1.0,
    "Loja Sorocaba": 0.8,
    "Loja Osasco": 0.95,
    "Loja Guarulhos": 1.05,
}

HISTORY_DAYS = 30


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        store_objs = []
        for name, city, state, lat, lon, is_cd in STORES:
            s = Store(name=name, city=city, state=state, latitude=lat, longitude=lon, is_distribution_center=is_cd)
            db.add(s)
            store_objs.append(s)
        db.flush()

        product_objs = []
        for sku, name, category, unit_cost, safety_days, _base_demand in PRODUCTS:
            p = Product(sku=sku, name=name, category=category, unit_cost=unit_cost, safety_stock_days=safety_days)
            db.add(p)
            product_objs.append(p)
        db.flush()

        today = date.today()

        for store in store_objs:
            factor = STORE_FACTOR[store.name]
            if factor == 0.0:
                continue  # CD nao mantem estoque de varejo para o consumidor final

            for (sku, name, category, unit_cost, safety_days, base_demand), product in zip(PRODUCTS, product_objs):
                avg_daily = max(1.0, base_demand * factor)

                # tendencia leve de crescimento/queda por produto+loja para dar sinal ao forecast
                trend = random.uniform(-0.015, 0.03)

                inv = Inventory(
                    store_id=store.id,
                    product_id=product.id,
                    quantity_on_hand=int(avg_daily * random.uniform(2, 6)),
                    reorder_point=int(avg_daily * safety_days),
                )
                db.add(inv)
                db.flush()

                for day_offset in range(HISTORY_DAYS, 0, -1):
                    sale_date = today - timedelta(days=day_offset)
                    day_index = HISTORY_DAYS - day_offset
                    weekday_boost = 1.35 if sale_date.weekday() in (5, 6) else 1.0  # fds vende mais (DIY)
                    trended = avg_daily * (1 + trend * day_index) * weekday_boost
                    noise = random.gauss(0, avg_daily * 0.2)
                    units = max(0, round(trended + noise))
                    db.add(SalesHistory(inventory_id=inv.id, sale_date=sale_date, units_sold=units))

        db.commit()
        print(f"Seed concluído: {len(store_objs)} lojas, {len(product_objs)} produtos, "
              f"{HISTORY_DAYS} dias de histórico de vendas.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
