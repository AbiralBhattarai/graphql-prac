from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import redis.asyncio as redis
from contextlib import asynccontextmanager

from src.adapters.graphql.schema import schema
from src.adapters.redis_adapter import RedisAdapter

# Global Redis client and adapter
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
redis_adapter = RedisAdapter(redis_client=redis_client)

def custom_context_dependency():
    return {
        "redis_adapter": redis_adapter
    }

async def get_context():
    return custom_context_dependency()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Any startup logic can go here
    yield
    # Teardown
    await redis_client.close()

app = FastAPI(lifespan=lifespan)

# Setup Strawberry router with context injection
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)

app.include_router(graphql_app, prefix="/graphql")
