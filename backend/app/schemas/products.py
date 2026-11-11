from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    brand: str | None
    category: str | None
    variant: str | None
    unit: str
    purchase_price_paise: int
    selling_price_paise: int
    stock_quantity: int
    low_stock_threshold: int
    image_url: str | None
    created_at: datetime

class StockAdjustment(BaseModel):
    quantity_change: int = Field(..., ne=0)
    reason: str = Field(default="Manual adjustment", max_length=120)
