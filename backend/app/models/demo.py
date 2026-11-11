from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class DemoShopMetrics(Base):
    __tablename__ = "demo_shop_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shop_name: Mapped[str] = mapped_column(String(120), default="Meri Kirana Store")
    today_sales_paise: Mapped[int] = mapped_column(Integer, default=545000)
    today_expenses_paise: Mapped[int] = mapped_column(Integer, default=120000)
    outstanding_credit_paise: Mapped[int] = mapped_column(Integer, default=850000)
    low_stock_items: Mapped[int] = mapped_column(Integer, default=7)
