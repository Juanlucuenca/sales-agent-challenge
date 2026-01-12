from typing import Optional, List
from pydantic import BaseModel
from pydantic_ai import RunContext


class CartItem(BaseModel):
    product_id: int
    quantity: int


async def get_categories(ctx: RunContext, skip: int = 0, limit: int = 100) -> dict:
    try:
        response = await ctx.deps.http_client.get(
            f"{ctx.deps.api_base_url}/categories",
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return {"categories": response.json()}
    except Exception as e:
        return {"error": str(e)}


async def get_products(
    ctx: RunContext,
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = True
) -> dict:
    try:
        params = {"skip": skip, "limit": limit}
        if category_id is not None:
            params["category_id"] = category_id
        if is_active is not None:
            params["is_active"] = is_active
            
        response = await ctx.deps.http_client.get(
            f"{ctx.deps.api_base_url}/products",
            params=params
        )
        response.raise_for_status()
        return {"products": response.json()}
    except Exception as e:
        return {"error": str(e)}


async def get_product_by_id(ctx: RunContext, product_id: int) -> dict:
    try:
        response = await ctx.deps.http_client.get(
            f"{ctx.deps.api_base_url}/products/{product_id}"
        )
        if response.status_code == 404:
            return {"error": f"Product with id {product_id} not found"}
        response.raise_for_status()
        return {"product": response.json()}
    except Exception as e:
        return {"error": str(e)}


async def get_cart(ctx: RunContext) -> dict:
    try:
        response = await ctx.deps.http_client.get(
            f"{ctx.deps.api_base_url}/carts/phone/{ctx.deps.user_phone}"
        )
        response.raise_for_status()
        return {"cart": response.json()}
    except Exception as e:
        return {"error": str(e)}


async def add_to_cart(ctx: RunContext, items: List[CartItem]) -> dict:
    try:
        cart_response = await ctx.deps.http_client.get(
            f"{ctx.deps.api_base_url}/carts/phone/{ctx.deps.user_phone}"
        )
        if cart_response.status_code != 200:
            return {"error": "Could not find cart"}
        
        cart = cart_response.json()
        cart_id = cart["id"]
        
        existing_items = {item["product_id"]: item["quantity"] for item in cart.get("cart_items", [])}
        
        for item in items:
            if item.product_id in existing_items:
                existing_items[item.product_id] += item.quantity
            else:
                existing_items[item.product_id] = item.quantity
        
        payload = {
            "items": [{"product_id": pid, "quantity": qty} for pid, qty in existing_items.items() if qty > 0]
        }
        
        response = await ctx.deps.http_client.put(
            f"{ctx.deps.api_base_url}/carts/{cart_id}",
            json=payload
        )
        if response.status_code == 400:
            return {"error": response.json().get("detail", "Bad request")}
        if response.status_code == 404:
            return {"error": response.json().get("detail", "Product not found")}
        response.raise_for_status()
        return {"cart": response.json()}
    except Exception as e:
        return {"error": str(e)}


async def update_cart(ctx: RunContext, items: List[CartItem]) -> dict:
    try:
        cart_response = await ctx.deps.http_client.get(
            f"{ctx.deps.api_base_url}/carts/phone/{ctx.deps.user_phone}"
        )
        if cart_response.status_code != 200:
            return {"error": "Could not find cart"}
        
        cart_id = cart_response.json()["id"]
        
        payload = {
            "items": [{"product_id": item.product_id, "quantity": item.quantity} for item in items]
        }
        response = await ctx.deps.http_client.put(
            f"{ctx.deps.api_base_url}/carts/{cart_id}",
            json=payload
        )
        if response.status_code == 404:
            return {"error": response.json().get("detail", "Cart not found")}
        if response.status_code == 400:
            return {"error": response.json().get("detail", "Bad request")}
        response.raise_for_status()
        return {"cart": response.json()}
    except Exception as e:
        return {"error": str(e)}
