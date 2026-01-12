import logging
import sys
import fastapi
from contextlib import asynccontextmanager
from db.con import Base, engine
from db.schemas import Category, Product, Cart, CartsItems, Conversation
from router.products.router import router as products_router
from router.categories.router import router as categories_router
from router.carts.router import router as carts_router
from router.chat.router import router as chat_router
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()
logfire.instrument_httpx(capture_all=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logfire.LogfireLoggingHandler()],
)

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    logger.info("App lifespan started")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
    yield
    logger.info("App shutting down")

app = fastapi.FastAPI(lifespan=lifespan)

app.include_router(products_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(carts_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")

logfire.instrument_fastapi(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
