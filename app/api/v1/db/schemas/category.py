from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from db.con import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, index=True)
    products = relationship("Product", back_populates="category")