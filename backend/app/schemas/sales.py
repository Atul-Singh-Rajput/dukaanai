from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class SaleItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=10000)

class SaleCreate(BaseModel):
    items: list[SaleItemIn] = Field(min_length=1)
    discount_paise: int = Field(default=0, ge=0)
    payment_method: str = Field(pattern="^(cash|upi|credit)$")
    amount_received_paise: int | None = Field(default=None, ge=0)
    customer_name: str | None = Field(default=None, max_length=120)

class SaleItemOut(BaseModel):
    product_id: int
    product_name: str
    unit: str
    quantity: int
    unit_price_paise: int
    line_total_paise: int
    model_config = ConfigDict(from_attributes=True)

class SaleOut(BaseModel):
    id: int
    invoice_number: str
    subtotal_paise: int
    discount_paise: int
    total_paise: int
    payment_method: str
    amount_received_paise: int
    change_paise: int
    customer_name: str | None
    created_at: datetime
    items: list[SaleItemOut]
    model_config = ConfigDict(from_attributes=True)
