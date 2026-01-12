from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.con import Base

class CartsItems(Base):
    __tablename__ = "carts_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")