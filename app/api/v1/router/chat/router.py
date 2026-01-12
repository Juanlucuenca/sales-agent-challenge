from fastapi import APIRouter, Form, Response, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from twilio.rest import Client
import logging
import traceback

from agent.main import run_sales_agent
from db.con import get_db, SessionLocal
from core.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

twilio_client = Client(settings.twilio_account_sid, settings.twilio_auth_token)


async def process_and_send_message(phone_number: str, message: str):
    db = SessionLocal()
    try:
        agent_response = await run_sales_agent(
            user_message=message,
            user_phone=phone_number,
            db_session=db
        )
        
        response_text = agent_response.response
        logger.info(f"Sending response to {phone_number}: {response_text[:100]}...")
        
        twilio_client.messages.create(
            body=response_text,
            from_=f"whatsapp:{settings.twilio_phone_number}",
            to=f"whatsapp:{phone_number}"
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        logger.error(traceback.format_exc())
        try:
            twilio_client.messages.create(
                body="Lo siento, hubo un error procesando tu mensaje. Intenta de nuevo.",
                from_=f"whatsapp:{settings.twilio_phone_number}",
                to=f"whatsapp:{phone_number}"
            )
        except Exception as send_error:
            logger.error(f"Error sending error message: {send_error}")
    finally:
        db.close()


@router.post("/webhook/twilio")
async def twilio_webhook(
    background_tasks: BackgroundTasks,
    Body: str = Form(...),
    From: str = Form(...),
    db: Session = Depends(get_db),
):
    phone_number = From.replace("whatsapp:", "")
    logger.info(f"Received message from {phone_number}: {Body}")
    
    background_tasks.add_task(process_and_send_message, phone_number, Body)
    
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )
