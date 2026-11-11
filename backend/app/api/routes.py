from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.demo import DemoShopMetrics
from app.models.product import Product, StockMovement
from app.schemas.dashboard import DashboardResponse
from app.schemas.products import ProductOut, StockAdjustment
from app.models.sale import Sale, SaleItem
from app.schemas.sales import SaleCreate, SaleOut
from datetime import datetime
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/api/v1", tags=["DukaanAI"])
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    metrics = db.query(DemoShopMetrics).first()
    if metrics is None:
        metrics = DemoShopMetrics()
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
    return DashboardResponse(
        shop_name=metrics.shop_name,
        today_sales_paise=metrics.today_sales_paise,
        today_expenses_paise=metrics.today_expenses_paise,
        outstanding_credit_paise=metrics.outstanding_credit_paise,
        low_stock_items=metrics.low_stock_items,
        demo_data=True,
    )

@router.get("/products", response_model=list[ProductOut])
def list_products(q: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Product)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter((Product.name.ilike(term)) | (Product.brand.ilike(term)) | (Product.category.ilike(term)))
    return query.order_by(Product.name.asc()).all()

@router.post("/products", response_model=ProductOut, status_code=201)
async def create_product(
    name: str = Form(...), brand: str = Form(""), category: str = Form(""),
    variant: str = Form(""), unit: str = Form("piece"),
    purchase_price_paise: int = Form(0), selling_price_paise: int = Form(0),
    stock_quantity: int = Form(0), low_stock_threshold: int = Form(5),
    image: UploadFile | None = File(None), db: Session = Depends(get_db),
):
    clean_name = name.strip()
    if not clean_name:
        raise HTTPException(400, "Product name is required")
    if min(purchase_price_paise, selling_price_paise, stock_quantity, low_stock_threshold) < 0:
        raise HTTPException(400, "Prices and stock values cannot be negative")
    image_url = await save_image(image) if image else None
    product = Product(
        name=clean_name, brand=brand.strip() or None, category=category.strip() or None,
        variant=variant.strip() or None, unit=unit.strip() or "piece",
        purchase_price_paise=purchase_price_paise, selling_price_paise=selling_price_paise,
        stock_quantity=stock_quantity, low_stock_threshold=low_stock_threshold, image_url=image_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    if stock_quantity:
        db.add(StockMovement(product_id=product.id, quantity_change=stock_quantity, reason="Opening stock"))
        db.commit()
    return product

async def save_image(image: UploadFile) -> str:
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Only JPG, PNG and WEBP images are allowed")
    content = await image.read(MAX_IMAGE_BYTES + 1)
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(400, "Image must be 5 MB or smaller")
    if not content:
        raise HTTPException(400, "Uploaded image is empty")
    filename = f"{uuid4().hex}{ALLOWED_TYPES[image.content_type]}"
    (UPLOAD_DIR / filename).write_bytes(content)
    return f"/uploads/{filename}"

@router.put("/products/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int, name: str = Form(...), brand: str = Form(""), category: str = Form(""),
    variant: str = Form(""), unit: str = Form("piece"),
    purchase_price_paise: int = Form(0), selling_price_paise: int = Form(0),
    stock_quantity: int = Form(0), low_stock_threshold: int = Form(5),
    image: UploadFile | None = File(None), db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    if not name.strip() or min(purchase_price_paise, selling_price_paise, stock_quantity, low_stock_threshold) < 0:
        raise HTTPException(400, "Enter a product name and non-negative values")
    previous_stock = product.stock_quantity
    product.name, product.brand, product.category = name.strip(), brand.strip() or None, category.strip() or None
    product.variant, product.unit = variant.strip() or None, unit.strip() or "piece"
    product.purchase_price_paise, product.selling_price_paise = purchase_price_paise, selling_price_paise
    product.stock_quantity, product.low_stock_threshold = stock_quantity, low_stock_threshold
    if stock_quantity != previous_stock:
        db.add(StockMovement(product_id=product_id, quantity_change=stock_quantity - previous_stock, reason="Stock changed while editing product"))
    if image:
        product.image_url = await save_image(image)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    db.query(StockMovement).filter(StockMovement.product_id == product_id).delete()
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}

@router.post("/products/{product_id}/stock", response_model=ProductOut)
def adjust_stock(product_id: int, adjustment: StockAdjustment, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    new_quantity = product.stock_quantity + adjustment.quantity_change
    if new_quantity < 0:
        raise HTTPException(400, "Stock cannot become negative")
    product.stock_quantity = new_quantity
    db.add(StockMovement(product_id=product_id, quantity_change=adjustment.quantity_change, reason=adjustment.reason))
    db.commit()
    db.refresh(product)
    return product

@router.get("/stock/movements")
def list_stock_movements(db: Session = Depends(get_db)):
    rows = db.query(StockMovement, Product.name).join(Product, Product.id == StockMovement.product_id).order_by(StockMovement.created_at.desc()).limit(100).all()
    return [{"id": m.id, "product_id": m.product_id, "product_name": name, "quantity_change": m.quantity_change, "reason": m.reason, "created_at": m.created_at} for m, name in rows]


@router.post("/sales", response_model=SaleOut, status_code=201)
def create_sale(payload: SaleCreate, db: Session = Depends(get_db)):
    if payload.discount_paise < 0:
        raise HTTPException(400, "Discount cannot be negative")
    # Combine duplicate product rows so stock is checked and deducted exactly once.
    quantities: dict[int, int] = {}
    for item in payload.items:
        quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity
    products: dict[int, Product] = {}
    subtotal = 0
    sale_items = []
    for product_id, quantity in quantities.items():
        product = db.get(Product, product_id)
        if product is None:
            raise HTTPException(404, f"Product {product_id} not found")
        if product.stock_quantity < quantity:
            raise HTTPException(400, f"Insufficient stock for {product.name}. Available: {product.stock_quantity}")
        line_total = product.selling_price_paise * quantity
        subtotal += line_total
        products[product_id] = product
        sale_items.append(SaleItem(product_id=product.id, product_name=product.name, unit=product.unit, quantity=quantity, unit_price_paise=product.selling_price_paise, line_total_paise=line_total))
    if payload.discount_paise > subtotal:
        raise HTTPException(400, "Discount cannot exceed subtotal")
    total = subtotal - payload.discount_paise
    received = payload.amount_received_paise if payload.amount_received_paise is not None else total
    if payload.payment_method != "credit" and received < total:
        raise HTTPException(400, "Amount received is less than the bill total")
    if payload.payment_method == "credit":
        received = 0
    invoice = f"DA-{datetime.now().strftime('%y%m%d')}-{uuid4().hex[:6].upper()}"
    sale = Sale(invoice_number=invoice, subtotal_paise=subtotal, discount_paise=payload.discount_paise, total_paise=total, payment_method=payload.payment_method, amount_received_paise=received, change_paise=max(0, received-total), customer_name=payload.customer_name.strip() if payload.customer_name else None, items=sale_items)
    try:
        for product_id, quantity in quantities.items():
            product = products[product_id]
            product.stock_quantity -= quantity
            db.add(StockMovement(product_id=product_id, quantity_change=-quantity, reason=f"Sale {invoice}"))
        db.add(sale)
        db.commit()
        db.refresh(sale)
        return sale
    except Exception:
        db.rollback()
        raise

@router.get("/sales", response_model=list[SaleOut])
def list_sales(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Sale).order_by(Sale.created_at.desc()).limit(min(max(limit, 1), 100)).all()

@router.get("/sales/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.get(Sale, sale_id)
    if not sale:
        raise HTTPException(404, "Sale not found")
    return sale
