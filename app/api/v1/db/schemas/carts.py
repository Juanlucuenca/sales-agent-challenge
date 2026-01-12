from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from db.con import Base


class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    cart_items = relationship("CartsItems", back_populates="cart")