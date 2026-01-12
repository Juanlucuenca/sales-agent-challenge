from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from pydantic_core import to_jsonable_python
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter

from db.schemas.conversations import Conversation
from db.schemas.carts import Cart


def get_or_create_conversation(db: Session, phone_number: str) -> Conversation:
    """Get existing conversation or create new one for phone number. Also creates empty cart."""
    conversation = db.query(Conversation).filter(
        Conversation.phone_number == phone_number
    ).first()
    
    if not conversation:
        conversation = Conversation(phone_number=phone_number, messages=[])
        db.add(conversation)
        
        existing_cart = db.query(Cart).filter(Cart.phone_number == phone_number).first()
        if not existing_cart:
            now = datetime.utcnow()
            cart = Cart(phone_number=phone_number, created_at=now, updated_at=now)
            db.add(cart)
        
        db.commit()
        db.refresh(conversation)
    
    return conversation


def load_message_history(conversation: Conversation, limit: int = 8) -> List[ModelMessage]:
    """Load message history from conversation JSON."""
    if not conversation.messages:
        return []
    
    raw_messages = conversation.messages[-limit:] if len(conversation.messages) > limit else conversation.messages
    
    if not raw_messages:
        return []
    
    # patch anthropic requires each tool_use to have its corresponding tool_result.
    start_idx = 0
    for i, msg in enumerate(raw_messages):
        if msg.get("kind") == "request":
            parts = msg.get("parts", [])
            has_tool_return = any(p.get("kind") == "tool-return" for p in parts)
            if not has_tool_return:
                start_idx = i
                break
    
    raw_messages = raw_messages[start_idx:]
    
    if not raw_messages:
        return []
    
    try:
        return ModelMessagesTypeAdapter.validate_python(raw_messages)
    except Exception:
        return []


def save_messages(db: Session, conversation: Conversation, new_messages: List[ModelMessage]) -> None:
    """Append new messages to conversation JSON."""
    current = list(conversation.messages or [])
    
    serialized = to_jsonable_python(new_messages)
    current.extend(serialized)
    
    conversation.messages = current
    flag_modified(conversation, "messages")
    db.commit()


def clear_history(db: Session, conversation: Conversation) -> None:
    """Clear conversation history."""
    conversation.messages = []
    flag_modified(conversation, "messages")
    db.commit()
