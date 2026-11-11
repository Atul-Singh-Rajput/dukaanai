from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    variant: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit: Mapped[str] = mapped_column(String(30), default="piece")
    purchase_price_paise: Mapped[int] = mapped_column(Integer, default=0)
    selling_price_paise: Mapped[int] = mapped_column(Integer, default=0)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=5)
    image_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    quantity_change: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(120), default="Manual adjustment")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
