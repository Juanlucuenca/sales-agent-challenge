from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CartCreate(BaseModel):
    phone_number: str = Field(min_length=1)
    items: Optional[List[CartItemBase]] = None


class CartUpdate(BaseModel):
    phone_number: Optional[str] = None
    items: Optional[List[CartItemBase]] = None


class CartResponse(BaseModel):
    id: int
    phone_number: str
    cart_items: List[CartItemResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
