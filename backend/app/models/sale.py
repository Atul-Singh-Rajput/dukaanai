from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class Sale(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    subtotal_paise: Mapped[int] = mapped_column(Integer)
    discount_paise: Mapped[int] = mapped_column(Integer, default=0)
    total_paise: Mapped[int] = mapped_column(Integer)
    payment_method: Mapped[str] = mapped_column(String(20))
    amount_received_paise: Mapped[int] = mapped_column(Integer)
    change_paise: Mapped[int] = mapped_column(Integer, default=0)
    customer_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale", cascade="all, delete-orphan")

class SaleItem(Base):
    __tablename__ = "sale_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), index=True)
    product_id: Mapped[int] = mapped_column(Integer)
    product_name: Mapped[str] = mapped_column(String(160))
    unit: Mapped[str] = mapped_column(String(30))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_paise: Mapped[int] = mapped_column(Integer)
    line_total_paise: Mapped[int] = mapped_column(Integer)
    sale: Mapped[Sale] = relationship(back_populates="items")
