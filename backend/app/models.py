from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_distribution_center = Column(Integer, default=0)  # 0/1 flag, CD = Centro de Distribuicao

    inventories = relationship("Inventory", back_populates="store")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    unit_cost = Column(Float, nullable=False)
    safety_stock_days = Column(Integer, default=3)

    inventories = relationship("Inventory", back_populates="product")


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (UniqueConstraint("store_id", "product_id", name="uix_store_product"),)

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_on_hand = Column(Integer, nullable=False, default=0)
    reorder_point = Column(Integer, nullable=False, default=10)

    store = relationship("Store", back_populates="inventories")
    product = relationship("Product", back_populates="inventories")
    sales_history = relationship("SalesHistory", back_populates="inventory")


class SalesHistory(Base):
    __tablename__ = "sales_history"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    sale_date = Column(Date, nullable=False)
    units_sold = Column(Integer, nullable=False)

    inventory = relationship("Inventory", back_populates="sales_history")
