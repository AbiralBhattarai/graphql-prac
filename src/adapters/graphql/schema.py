import asyncio
import uuid
import strawberry
from typing import AsyncGenerator
from src.domain.models.input import RawDataModel
from src.application.worker import process_worker

@strawberry.input
class RawDataInput:
    id: int
    name: str
    followers: int
    followings: int
    likes: int
    comments: int
    impressions: int
    has_bio: bool = True
    has_pfp: bool = False

@strawberry.type
class ProcessedData:
    id: int
    name: str
    followers: int
    followings: int
    likes: int
    comments: int
    impressions: int
    has_bio: bool
    has_pfp: bool
    likes_followers_ratio: float
    likes_comments_ratio: float
    likes_impressions_ratio: float
    task_id: str
    status: str

@strawberry.type
class TaskStatusResponse:
    task_id: str
    status: str

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "GraphQL Server is running."

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def process_data(self, info: strawberry.Info, raw_data: RawDataInput) -> TaskStatusResponse:
        redis_adapter = info.context["redis_adapter"]
        task_id = str(uuid.uuid4())
        
        # Save initial state
        initial_state = {"status": "pending"}
        await redis_adapter.set(f"task:{task_id}", initial_state)
        
        # Convert input to domain model
        raw_data_model = RawDataModel(
            id=raw_data.id,
            name=raw_data.name,
            followers=raw_data.followers,
            followings=raw_data.followings,
            likes=raw_data.likes,
            comments=raw_data.comments,
            impressions=raw_data.impressions,
            has_bio=raw_data.has_bio,
            has_pfp=raw_data.has_pfp
        )
        
        # Trigger background task
        asyncio.create_task(process_worker(task_id, raw_data_model, redis_adapter))
        
        return TaskStatusResponse(task_id=task_id, status="pending")

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def data_status(self, info: strawberry.Info, task_id: str) -> AsyncGenerator[ProcessedData, None]:
        redis_adapter = info.context["redis_adapter"]
        key = f"task:{task_id}"
        
        while True:
            data = await redis_adapter.get(key)
            if data and data.get("status") == "completed":
                yield ProcessedData(
                    id=int(data["id"]),
                    name=data["name"],
                    followers=int(data["followers"]),
                    followings=int(data["followings"]),
                    likes=int(data["likes"]),
                    comments=int(data["comments"]),
                    impressions=int(data["impressions"]),
                    has_bio=str(data["has_bio"]) == "True",
                    has_pfp=str(data["has_pfp"]) == "True",
                    likes_followers_ratio=float(data["likes_followers_ratio"]),
                    likes_comments_ratio=float(data["likes_comments_ratio"]),
                    likes_impressions_ratio=float(data["likes_impressions_ratio"]),
                    task_id=data["task_id"],
                    status=data["status"]
                )
                break
            elif data and data.get("status") == "failed":
                raise Exception(f"Task failed: {data.get('error')}")
                
            await asyncio.sleep(1)

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
