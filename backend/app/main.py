from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import Base, engine
from app.models.product import Product, StockMovement
from app.models.sale import Sale, SaleItem
from app.api.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.mount("/uploads", StaticFiles(directory=str(__import__("pathlib").Path(__file__).resolve().parent / "uploads")), name="uploads")

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "dukaanai-api"}
