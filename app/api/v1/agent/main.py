import httpx
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, ModelSettings
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from dataclasses import dataclass
from typing import Optional, List

from agent.prompt import SALES_AGENT_PROMPT
from agent.tools import (
    get_categories,
    get_products,
    get_product_by_id,
    get_cart,
    add_to_cart,
    update_cart,
    CartItem
)
from core.settings import settings


@dataclass
class SalesDeps:
    http_client: httpx.AsyncClient
    api_base_url: str
    user_phone: str


class ResponseModel(BaseModel):
    response: str = Field(description="The response to the user's message: MAX LENGHT 1500 CHARACTERS")

    class Config:
        from_attributes = True


model = OpenRouterModel(
    settings.openrouter_model,
    provider=OpenRouterProvider(api_key=settings.openrouter_apikey),
    settings=ModelSettings(temperature=0.1, max_tokens=350)
)

sales_agent = Agent(
    model,
    deps_type=SalesDeps,
    output_type=ResponseModel,
)


@sales_agent.system_prompt
def system_prompt() -> str:
    return SALES_AGENT_PROMPT


@sales_agent.tool
async def tool_get_categories(
    ctx: RunContext[SalesDeps],
    skip: int = 0,
    limit: int = 100
) -> dict:
    """
    Retrieve all available product categories from the database.
    
    Use this tool when the customer asks about available categories or types of products.
    
    Args:
        skip: Number of records to skip for pagination. Default: 0
        limit: Maximum number of categories to return. Default: 100
    """
    return await get_categories(ctx, skip, limit)


@sales_agent.tool
async def tool_get_products(
    ctx: RunContext[SalesDeps],
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = True
) -> dict:
    """
    Retrieve products from the database with optional filtering.
    
    Use this tool when the customer wants to see available products or browse the catalog.
    
    Args:
        skip: Number of records to skip for pagination. Default: 0
        limit: Maximum number of products to return. Default: 100
        category_id: Filter by category ID. Use None for all categories.
        is_active: Filter by active status. Default: True (only active products)
    """
    return await get_products(ctx, skip, limit, category_id, is_active)


@sales_agent.tool
async def tool_get_product_by_id(
    ctx: RunContext[SalesDeps],
    product_id: int
) -> dict:
    """
    Retrieve detailed information about a specific product.
    
    Use this tool when the customer asks about a specific product or you need details
    before adding to cart.
    
    Args:
        product_id: The unique identifier of the product to retrieve
    """
    return await get_product_by_id(ctx, product_id)


@sales_agent.tool
async def tool_get_cart(ctx: RunContext[SalesDeps]) -> dict:
    """
    Retrieve the current shopping cart for the user.
    
    Use this tool when the customer asks to see their cart, check their order,
    or before modifying existing cart items.
    
    The phone number is automatically obtained from the conversation context.
    """
    return await get_cart(ctx)


@sales_agent.tool
async def tool_add_to_cart(
    ctx: RunContext[SalesDeps],
    items: List[CartItem]
) -> dict:
    """
    Add items to the user's shopping cart.
    
    Use this tool when the customer wants to buy/purchase/add products.
    Items are added to existing cart items (quantities are summed).
    
    Args:
        items: List of items to add. Example: [{"product_id": 1, "quantity": 2}]
    """
    return await add_to_cart(ctx, items)


@sales_agent.tool
async def tool_update_cart(
    ctx: RunContext[SalesDeps],
    items: List[CartItem]
) -> dict:
    """
    Replace all items in the cart with a new list.
    
    Use this tool when the customer wants to:
    - Change quantities (set new amount)
    - Remove items (exclude from list)
    - Clear cart (pass empty list)
    
    IMPORTANT: This REPLACES all items, not adds.
    
    Args:
        items: Complete new list of items. Empty list = empty cart.
    """
    return await update_cart(ctx, items)


async def run_sales_agent(user_message: str, user_phone: str, db_session=None) -> str:
    """
    Run the sales agent with a user message and conversation memory.
    
    Args:
        user_message: The message from the user
        user_phone: The phone number of the user (for cart association)
        db_session: SQLAlchemy session for conversation persistence
    
    Returns:
        The agent's response as a string
    """
    from agent.history import get_or_create_conversation, load_message_history, save_messages
    
    message_history = []
    conversation = None
    
    if db_session:
        conversation = get_or_create_conversation(db_session, user_phone)
        message_history = load_message_history(conversation)
    
    async with httpx.AsyncClient() as client:
        deps = SalesDeps(
            http_client=client,
            api_base_url=settings.api_base_url,
            user_phone=user_phone
        )
        result = await sales_agent.run(
            user_message,
            deps=deps,
            message_history=message_history
        )
        
        if db_session and conversation:
            save_messages(db_session, conversation, result.new_messages())
        return result.output
