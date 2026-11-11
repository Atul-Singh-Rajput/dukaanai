from pydantic import BaseModel

class DashboardResponse(BaseModel):
    shop_name: str
    today_sales_paise: int
    today_expenses_paise: int
    outstanding_credit_paise: int
    low_stock_items: int
    demo_data: bool = True
