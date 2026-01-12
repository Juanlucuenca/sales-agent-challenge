import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from db.con import engine, SessionLocal, Base
from db.schemas import Product, Category

PRODUCTS_FILE = Path(__file__).parent / "data" / "products.xlsx"


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def extract_products() -> pd.DataFrame:
    return pd.read_excel(PRODUCTS_FILE)


def transform_categories(df: pd.DataFrame) -> list[dict]:
    categories = df["CATEGORÍA"].dropna().unique().tolist()
    now = datetime.now()
    return [{"name": cat, "created_at": now, "updated_at": now} for cat in categories]


def transform_products(df: pd.DataFrame, category_map: dict) -> list[dict]:
    now = datetime.now()
    products = []
    for _, row in df.iterrows():
        is_active = str(row.get("DISPONIBLE", "")).strip().lower() in ["sí", "si", "yes", "1", "true"]

        description_parts = []
        if pd.notna(row.get("DESCRIPCIÓN")):
            description_parts.append(str(row["DESCRIPCIÓN"]))
        if pd.notna(row.get("TALLA")):
            description_parts.append(f"Talla: {row['TALLA']}")
        if pd.notna(row.get("COLOR")):
            description_parts.append(f"Color: {row['COLOR']}")

        products.append({
            "name": str(row.get("TIPO_PRENDA", "")),
            "description": " | ".join(description_parts) if description_parts else "",
            "price": float(row.get("PRECIO_50_U", 0)),
            "stock": int(row.get("CANTIDAD_DISPONIBLE", 0)),
            "is_active": is_active,
            "category_id": category_map.get(row.get("CATEGORÍA")),
            "created_at": now,
            "updated_at": now,
        })
    return products


def load_categories(db: Session, categories: list[dict]) -> dict:
    category_map = {}
    for cat_data in categories:
        category = Category(**cat_data)
        db.add(category)
        db.flush()
        category_map[cat_data["name"]] = category.id
    db.commit()
    return category_map


def load_products(db: Session, products: list[dict]) -> int:
    for prod_data in products:
        db.add(Product(**prod_data))
    db.commit()
    return len(products)


def run_etl():
    reset_database()
    df = extract_products()

    db = SessionLocal()
    try:
        categories = transform_categories(df)
        category_map = load_categories(db, categories)
        products = transform_products(df, category_map)
        count = load_products(db, products)
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_etl()
