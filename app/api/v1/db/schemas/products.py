from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from db.con import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Float, index=True)
    stock = Column(Integer, index=True)
    is_active = Column(Boolean, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartsItems", back_populates="product")
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)