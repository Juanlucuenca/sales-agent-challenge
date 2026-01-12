from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from db.con import get_db
from db.schemas import Cart, CartsItems, Product
from models.carts import CartCreate, CartUpdate, CartResponse

router = APIRouter(prefix="/carts", tags=["Carts"])


@router.post("", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def create_cart(cart_data: CartCreate, db: Session = Depends(get_db)):
    existing_cart = db.query(Cart).filter(Cart.phone_number == cart_data.phone_number).first()
    if existing_cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cart already exists for phone number {cart_data.phone_number}"
        )
    
    now = datetime.utcnow()
    new_cart = Cart(
        phone_number=cart_data.phone_number,
        created_at=now,
        updated_at=now
    )
    db.add(new_cart)
    db.flush()
    
    if cart_data.items:
        for item in cart_data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {item.product_id} not found"
                )
            
            if product.stock < item.quantity:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {product.name}. Available: {product.stock}"
                )
            
            cart_item = CartsItems(
                cart_id=new_cart.id,
                product_id=item.product_id,
                quantity=item.quantity,
                created_at=now,
                updated_at=now
            )
            db.add(cart_item)
    
    db.commit()
    db.refresh(new_cart)
    
    cart = (
        db.query(Cart)
        .options(joinedload(Cart.cart_items))
        .filter(Cart.id == new_cart.id)
        .first()
    )
    
    return cart


@router.put("/{cart_id}", response_model=CartResponse)
def update_cart(cart_id: int, cart_data: CartUpdate, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart with id {cart_id} not found"
        )
    
    now = datetime.utcnow()
    
    if cart_data.phone_number is not None:
        existing = (
            db.query(Cart)
            .filter(Cart.phone_number == cart_data.phone_number, Cart.id != cart_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Phone number {cart_data.phone_number} is already associated with another cart"
            )
        cart.phone_number = cart_data.phone_number
    
    if cart_data.items is not None:
        db.query(CartsItems).filter(CartsItems.cart_id == cart_id).delete()
        
        for item in cart_data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {item.product_id} not found"
                )
            
            if product.stock < item.quantity:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {product.name}. Available: {product.stock}"
                )
            
            cart_item = CartsItems(
                cart_id=cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                created_at=now,
                updated_at=now
            )
            db.add(cart_item)
    
    cart.updated_at = now
    db.commit()
    db.refresh(cart)
    
    updated_cart = (
        db.query(Cart)
        .options(joinedload(Cart.cart_items))
        .filter(Cart.id == cart_id)
        .first()
    )
    
    return updated_cart


@router.get("/phone/{phone_number}", response_model=CartResponse)
def get_cart_by_phone(phone_number: str, db: Session = Depends(get_db)):
    cart = (
        db.query(Cart)
        .options(joinedload(Cart.cart_items))
        .filter(Cart.phone_number == phone_number)
        .first()
    )
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart not found for phone number {phone_number}"
        )
    
    return cart


@router.get("/{cart_id}", response_model=CartResponse)
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = (
        db.query(Cart)
        .options(joinedload(Cart.cart_items))
        .filter(Cart.id == cart_id)
        .first()
    )
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart with id {cart_id} not found"
        )
    
    return cart
